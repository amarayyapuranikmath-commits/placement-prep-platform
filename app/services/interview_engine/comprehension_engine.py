"""
AIRE Comprehension Engine
==========================
Implements:
    - SAD (#1) Semantic Answer Decomposition
    - CCG (#2) Concept Confidence Graph (weak/strong concept detection)

Zero-LLM-call by default; the LLM is only invoked (via the injected
GroqClientProtocol) to tag concepts in claim spans that the local
dictionary/fuzzy matcher could not resolve, and calls are batched --
never one call per claim.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Optional

from . import (
    AnswerLengthClass,
    AnswerObject,
    Claim,
    ConceptScore,
    ConceptStatus,
    GroqClientProtocol,
    QuestionMeta, 
    ReasoningType,
)
from .prompt_builder import PromptBuilder

try:
    from rapidfuzz import fuzz as _rapidfuzz_fuzz
    _HAS_RAPIDFUZZ = True
except ImportError:  # pragma: no cover - fallback path
    import difflib
    _HAS_RAPIDFUZZ = False


MIN_TOKENS = 8
FUZZY_MATCH_THRESHOLD = 85  # 0-100 scale
HEDGE_MARKERS = (
    "i think", "maybe", "not sure", "i guess", "probably", "i believe",
    "sort of", "kind of", "possibly", "i'm not certain", "not 100% sure",
)
DISCOURSE_SPLIT_PATTERN = re.compile(
    r"(?<=[.!?])\s+|\s+(?:because|which means|so that|and then|however)\s+",
    re.IGNORECASE,
)
CODE_HINT_PATTERN = re.compile(
    r"(```[\s\S]*?```)|(\bdef\s+\w+\s*\()|(\bSELECT\b.+\bFROM\b)|(=>|\bfunction\s*\()",
    re.IGNORECASE,
)
CAUSAL_CONNECTOR_PATTERN = re.compile(
    r"\bbecause\b|\bwhich (allows|means|causes)\b|\bso that\b|\btherefore\b|\bwhich results in\b",
    re.IGNORECASE,
)
EXAMPLE_MARKER_PATTERN = re.compile(
    r"\bfor example\b|\be\.g\.\b|\bfor instance\b|\blike when\b", re.IGNORECASE
)


def _fuzzy_score(a: str, b: str) -> float:
    if _HAS_RAPIDFUZZ:
        return _rapidfuzz_fuzz.token_set_ratio(a, b)
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100


class ComprehensionEngine:
    """
    Concept dictionaries should be loaded once per topic and cached at the
    application layer (Redis / in-memory singleton), not re-fetched per call.
    Pass an initial mapping in via the constructor, or call
    `load_concept_dictionary` at startup.
    """

    def __init__(
        self,
        groq_client: GroqClientProtocol,
        prompt_builder: Optional[PromptBuilder] = None,
        concept_dictionary: Optional[dict[str, dict[str, list[str]]]] = None,
    ) -> None:
        self._groq = groq_client
        self._prompts = prompt_builder or PromptBuilder()
        # topic -> {concept_name: [synonym, ...]}
        self._concept_dictionary: dict[str, dict[str, list[str]]] = concept_dictionary or {}

    def load_concept_dictionary(self, topic: str, mapping: dict[str, list[str]]) -> None:
        self._concept_dictionary[topic] = mapping

    # ------------------------------------------------------------------ #
    # SAD (#1)
    # ------------------------------------------------------------------ #

    async def understand_answer(self, raw_answer: str, question: QuestionMeta) -> AnswerObject:
        tokens = raw_answer.split()

        if len(tokens) < MIN_TOKENS:
            return AnswerObject(
                raw_text=raw_answer,
                cleaned_text=raw_answer.strip(),
                claims=[],
                mentioned_concepts=set(),
                answer_length_class=AnswerLengthClass.TOO_SHORT,
            )

        code_blocks = self._extract_code(raw_answer)
        prose = self._remove_code(raw_answer, code_blocks)
        cleaned = prose.strip()

        raw_claims = self._split_into_claims(cleaned)
        concept_dict = self._concept_dictionary.get(question.topic, {})
        if not concept_dict:
            concept_dict = self._build_fallback_concept_dictionary(question)

        tagged_claims: list[Claim] = []
        unmatched: list[tuple[str, str]] = []  # (claim_id, claim_text)

        for text in raw_claims:
            claim_id = uuid.uuid4().hex[:8]
            matched = self._dictionary_match(text, concept_dict)
            hedge = self._hedge_score(text)
            if matched:
                tagged_claims.append(
                    Claim(id=claim_id, text=text, concepts=matched, confidence="high", hedge_score=hedge)
                )
            else:
                tagged_claims.append(
                    Claim(id=claim_id, text=text, concepts=[], confidence="medium", hedge_score=hedge)
                )
                unmatched.append((claim_id, text))

        # Conservative optimization: attempt a safe local fuzzy-match fallback
        # before invoking the LLM. This avoids a Groq call for trivial/unambiguous
        # unmatched spans while preserving accuracy for genuinely ambiguous text.
        if unmatched:
            expected_names = [c.get("name") for c in question.expected_concepts]
            expected_names += [c.get("name") for c in question.core_concepts]
            expected_names = [name for name in expected_names if name]

            remaining: list[tuple[str, str]] = []
            by_id = {c.id: c for c in tagged_claims}

            # First pass: try a lower-threshold fuzzy match locally.
            LOCAL_FUZZY_THRESHOLD = max(60, FUZZY_MATCH_THRESHOLD - 20)
            for claim_id, text in unmatched:
                local_matches = []
                for name in expected_names:
                    if _fuzzy_score(text, name) >= LOCAL_FUZZY_THRESHOLD:
                        local_matches.append(name)

                if local_matches:
                    # Assign locally-detected matches (lower confidence).
                    if claim_id in by_id:
                        by_id[claim_id].concepts = local_matches
                else:
                    remaining.append((claim_id, text))

            # Decide whether to call the LLM: only when there's more than one
            # unresolved span, or when a single unresolved span is long/complex.
            should_call_llm = False
            if len(remaining) >= 2:
                should_call_llm = True
            elif len(remaining) == 1:
                # If the remaining claim is long, prefer LLM interpretation.
                _, rem_text = remaining[0]
                if len(rem_text.split()) > 25:
                    should_call_llm = True

            if should_call_llm:
                llm_tags = await self._tag_unmatched_spans(remaining, expected_names)
                for claim_id, concepts in llm_tags.items():
                    if claim_id in by_id:
                        by_id[claim_id].concepts = concepts

        mentioned = {c for claim in tagged_claims for c in claim.concepts}
        reasoning_type = self._classify_reasoning_type(cleaned, bool(code_blocks))
        overall_hedge = (
            sum(c.hedge_score for c in tagged_claims) / len(tagged_claims) if tagged_claims else 0.0
        )
        filler_ratio = self._filler_ratio(cleaned)
        length_class = (
            AnswerLengthClass.VERBOSE if len(tokens) > 180 else AnswerLengthClass.ADEQUATE
        )

        return AnswerObject(
            raw_text=raw_answer,
            cleaned_text=cleaned,
            claims=tagged_claims,
            mentioned_concepts=mentioned,
            code_present=bool(code_blocks),
            code_blocks=code_blocks,
            reasoning_type=reasoning_type,
            hedge_score=overall_hedge,
            filler_ratio=filler_ratio,
            answer_length_class=length_class,
        )

    async def _tag_unmatched_spans(
        self, unmatched: list[tuple[str, str]], expected_concepts: list[str]
    ) -> dict[str, list[str]]:
        """One batched Groq call for every unmatched claim span -- never one call per claim."""
        messages = self._prompts.concept_tagging_prompt(unmatched, expected_concepts)
        raw = await self._groq.complete(messages, max_tokens=400, temperature=0.0, json_mode=True)
        return self._prompts.parse_concept_tagging_response(raw, [cid for cid, _ in unmatched])

    def _extract_code(self, text: str) -> list[str]:
        return [m.group(0) for m in CODE_HINT_PATTERN.finditer(text)]

    def _remove_code(self, text: str, code_blocks: list[str]) -> str:
        result = text
        for block in code_blocks:
            result = result.replace(block, " ")
        return result

    def _split_into_claims(self, text: str) -> list[str]:
        parts = [p.strip(" ,;") for p in DISCOURSE_SPLIT_PATTERN.split(text)]
        return [p for p in parts if p]

    def _build_fallback_concept_dictionary(self, question: QuestionMeta) -> dict[str, list[str]]:
        fallback: dict[str, list[str]] = {}
        for concept in question.expected_concepts or []:
            name = concept.get("name")
            if not name:
                continue
            fallback[name] = [name]
        for concept in question.core_concepts or []:
            name = concept.get("name")
            if not name or name in fallback:
                continue
            fallback[name] = [name]
        return fallback

    def _dictionary_match(self, claim_text: str, concept_dict: dict[str, list[str]]) -> list[str]:
        matches = []
        lowered = claim_text.lower()
        normalized_claim = self._normalize_text(lowered)
        claim_tokens = set(normalized_claim.split())

        for concept, synonyms in concept_dict.items():
            candidates = [concept] + list(synonyms)
            concept_tokens = set()
            for cand in candidates:
                concept_tokens.update(self._normalize_text(cand.lower()).split())

            if not concept_tokens:
                continue

            token_overlap = bool(claim_tokens & concept_tokens)
            term_overlap = any(term in normalized_claim for term in self._normalize_text(concept.lower()).split())
            fuzzy_match = any(
                _fuzzy_score(normalized_claim, self._normalize_text(cand.lower())) >= FUZZY_MATCH_THRESHOLD
                for cand in candidates
            )

            if token_overlap or term_overlap or fuzzy_match:
                matches.append(concept)
        return matches

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _hedge_score(self, claim_text: str) -> float:
        lowered = claim_text.lower()
        hits = sum(1 for marker in HEDGE_MARKERS if marker in lowered)
        return min(1.0, hits * 0.5)

    def _classify_reasoning_type(self, text: str, code_present: bool) -> ReasoningType:
        lowered = text.lower()
        if code_present and len(text) < 40:
            return ReasoningType.CODE
        has_example = bool(EXAMPLE_MARKER_PATTERN.search(lowered))
        has_causal = bool(CAUSAL_CONNECTOR_PATTERN.search(lowered))
        has_comparison = any(w in lowered for w in (" vs ", " versus ", "compared to", "whereas"))
        has_tradeoff = any(w in lowered for w in ("tradeoff", "trade-off", "on the other hand", "downside"))

        flags = [has_example, has_causal, has_comparison, has_tradeoff, code_present]
        if sum(bool(f) for f in flags) >= 2:
            return ReasoningType.MIXED
        if has_tradeoff:
            return ReasoningType.TRADEOFF
        if has_comparison:
            return ReasoningType.COMPARISON
        if has_example:
            return ReasoningType.EXAMPLE
        if has_causal:
            return ReasoningType.EXPLANATION
        if code_present:
            return ReasoningType.CODE
        return ReasoningType.DEFINITION

    def _filler_ratio(self, text: str) -> float:
        filler_words = {"um", "uh", "like", "basically", "actually", "you know"}
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return 0.0
        fillers = sum(1 for t in tokens if t in filler_words)
        return fillers / len(tokens)

    # ------------------------------------------------------------------ #
    # CCG (#2) -- pure logic, no LLM call
    # ------------------------------------------------------------------ #

    def score_concepts(
        self,
        answer: AnswerObject,
        question: QuestionMeta,
        candidate_history: Optional[dict[str, Any]] = None,
    ) -> dict[str, ConceptScore]:
        candidate_history = candidate_history or {}
        weak_streaks: dict[str, int] = candidate_history.get("weak_streaks", {})
        score_map: dict[str, ConceptScore] = {}

        scored_names: list[str] = []
        seen: set[str] = set()
        for concept in question.expected_concepts + question.core_concepts:
            name = concept["name"]
            if name and name not in seen:
                scored_names.append(name)
                seen.add(name)

        for name in scored_names:
            claims = [c for c in answer.claims if name in c.concepts]

            if not claims:
                score_map[name] = ConceptScore(concept=name, status=ConceptStatus.ABSENT, score=0.0)
                continue

            has_explanation = any(CAUSAL_CONNECTOR_PATTERN.search(c.text) for c in claims)
            has_example = any(EXAMPLE_MARKER_PATTERN.search(c.text) for c in claims)
            has_valid_code = answer.code_present and name.lower() in answer.cleaned_text.lower()
            contradicted = self._detect_contradiction(claims)
            avg_hedge = sum(c.hedge_score for c in claims) / len(claims)

            if contradicted:
                status, score = ConceptStatus.WEAK, 0.2
            elif has_explanation and (has_example or has_valid_code):
                status, score = ConceptStatus.STRONG, 0.9
            elif has_explanation:
                status, score = ConceptStatus.PARTIAL, 0.6
            elif avg_hedge > 0.5:
                status, score = ConceptStatus.WEAK, 0.3
            else:
                status, score = ConceptStatus.PARTIAL, 0.5

            if weak_streaks.get(name, 0) >= 2 and status == ConceptStatus.STRONG:
                status, score = ConceptStatus.PARTIAL, min(score, 0.6)

            score_map[name] = ConceptScore(
                concept=name, status=status, score=score, evidence_claim_ids=[c.id for c in claims]
            )

        return score_map

    def _detect_contradiction(self, claims: list[Claim]) -> bool:
        """Heuristic: a negation marker in one claim directly opposing another claim's assertion."""
        negations = ("not", "isn't", "doesn't", "never", "cannot", "can't")
        texts = [c.text.lower() for c in claims]
        has_negated = any(any(n in t for n in negations) for t in texts)
        has_affirmed = any(not any(n in t for n in negations) for t in texts)
        return has_negated and has_affirmed and len(texts) > 1