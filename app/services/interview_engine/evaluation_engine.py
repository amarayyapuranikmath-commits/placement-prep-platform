"""
AIRE Evaluation Engine
=======================
Implements:
    - CSE (#3) Correctness Scoring Engine
    - GDM (#4) Gap Detection Module

Deterministic-first: the LLM (via GroqClientProtocol) is only invoked as a
tiebreaker when core_coverage falls in the ambiguous band, and its output is
blended into the deterministic score rather than trusted alone.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from . import (
    AnswerLengthClass,
    AnswerObject,
    ConceptScore,
    ConceptStatus,
    CorrectnessVerdict,
    Gap,
    GapType,
    GroqClientProtocol,
    QuestionMeta,
    Verdict,
)
from .prompt_builder import PromptBuilder

AMBIGUOUS_BAND = (0.35, 0.55)
CORRECT_THRESHOLD = 0.8
INCORRECT_THRESHOLD = 0.4
MISCONCEPTION_PENALTY = 10.0
LLM_BLEND_WEIGHT = 0.3
MAX_GAPS_PER_TURN = 2


class EvaluationEngine:
    def __init__(self, groq_client: GroqClientProtocol, prompt_builder: Optional[PromptBuilder] = None) -> None:
        self._groq = groq_client
        self._prompts = prompt_builder or PromptBuilder()

    async def evaluate_answer(
        self,
        question: QuestionMeta,
        raw_answer: str,
        state: Any,
    ) -> dict[str, Any]:
        """Compatibility adapter for the legacy orchestrator contract.

        The modern InterviewOrchestrator reads a dict-shaped evaluation payload
        from `self.evaluation.evaluate_answer(...)`. The legacy `EvaluationEngine`
        is a deterministic scoring component and lacks that method, so the adapter
        emits a small schema-conforming fallback payload rather than exploding.
        """
        concepts = [c.get("name") for c in (question.core_concepts or question.expected_concepts or []) if c.get("name")]
        missing = [name for name in concepts if name and name.lower() not in raw_answer.lower()]
        return {
            "overall_score": 35,
            "verdict": "incorrect",
            "technical_accuracy": 35,
            "communication": 35,
            "concept_coverage": 35,
            "strengths": [],
            "weaknesses": ["Unable to invoke the evaluation service; no facts were emitted."],
            "missing_concepts": missing,
            "recommendations": ["Increase answer specificity and cover each expected concept."],
            "follow_up_question": "Can you explain the key concept using the interview question's wording?",
            "reasoning": "Fallback rule-based evaluation used because the intelligence provider is unavailable.",
            "hiring_signal": "neutral",
        }

    # ------------------------------------------------------------------ #
    # CSE (#3)
    # ------------------------------------------------------------------ #

    async def evaluate_correctness(
        self,
        concept_scores: dict[str, ConceptScore],
        question: QuestionMeta,
        answer: AnswerObject,
    ) -> CorrectnessVerdict:
        core_weighted = question.core_concepts or question.expected_concepts
        core_names = [c["name"] for c in core_weighted]
        core_coverage = self._weighted_average(concept_scores, core_weighted)
        misconceptions = self._detect_misconceptions(answer, question)

        if self._is_disjoint(answer.mentioned_concepts, core_names) and not answer.code_present:
            return CorrectnessVerdict(
                verdict=Verdict.OFF_TOPIC,
                score=0.0,
                core_coverage=0.0,
                misconceptions_triggered=misconceptions,
                rationale_tags=["disjoint_from_core"],
            )

        used_llm = False
        if AMBIGUOUS_BAND[0] <= core_coverage <= AMBIGUOUS_BAND[1]:
            llm_score = await self._llm_factuality_check(answer, question)
            if llm_score is not None:
                core_coverage = (1 - LLM_BLEND_WEIGHT) * core_coverage + LLM_BLEND_WEIGHT * llm_score
                used_llm = True

        if core_coverage >= CORRECT_THRESHOLD and not misconceptions:
            verdict = Verdict.CORRECT
        elif core_coverage < INCORRECT_THRESHOLD:
            verdict = Verdict.INCORRECT
        else:
            verdict = Verdict.PARTIALLY_CORRECT

        score = max(0.0, round(core_coverage * 100 - MISCONCEPTION_PENALTY * len(misconceptions), 1))
        tags = self._build_rationale_tags(core_coverage, misconceptions, used_llm)

        return CorrectnessVerdict(
            verdict=verdict,
            score=score,
            core_coverage=core_coverage,
            misconceptions_triggered=misconceptions,
            rationale_tags=tags,
            used_llm_tiebreak=used_llm,
        )

    async def _llm_factuality_check(self, answer: AnswerObject, question: QuestionMeta) -> Optional[float]:
        messages = self._prompts.factuality_check_prompt(answer.cleaned_text, question)
        raw = await self._groq.complete(messages, max_tokens=120, temperature=0.0, json_mode=True)
        return self._prompts.parse_factuality_response(raw)

    @staticmethod
    def answer_length_class_from_answer(raw_answer: str) -> AnswerLengthClass:
        tokens = raw_answer.split()
        if len(tokens) < 8:
            return AnswerLengthClass.TOO_SHORT
        if len(tokens) > 180:
            return AnswerLengthClass.VERBOSE
        return AnswerLengthClass.ADEQUATE

    def _weighted_average(
        self, concept_scores: dict[str, ConceptScore], weighted_concepts: list[dict[str, Any]]
    ) -> float:
        if not weighted_concepts:
            return 0.0
        total_weight = sum(c.get("weight", 1.0) for c in weighted_concepts)
        if total_weight == 0:
            return 0.0
        acc = 0.0
        for c in weighted_concepts:
            cs = concept_scores.get(c["name"])
            acc += (cs.score if cs else 0.0) * c.get("weight", 1.0)
        return acc / total_weight

    def _detect_misconceptions(self, answer: AnswerObject, question: QuestionMeta) -> list[str]:
        triggered = []
        for m in question.common_misconceptions:
            pattern = m.get("pattern")
            name = m.get("name", pattern)
            if not pattern:
                continue
            if re.search(pattern, answer.cleaned_text, re.IGNORECASE):
                triggered.append(name)
        return triggered

    def _is_disjoint(self, mentioned: set[str], expected: list[str]) -> bool:
        return len(mentioned.intersection(expected)) == 0

    def _build_rationale_tags(self, core_coverage: float, misconceptions: list[str], used_llm: bool) -> list[str]:
        tags = [f"core_coverage={core_coverage:.2f}"]
        if misconceptions:
            tags.append(f"misconceptions={len(misconceptions)}")
        if used_llm:
            tags.append("llm_tiebreak_used")
        return tags

    # ------------------------------------------------------------------ #
    # GDM (#4) -- pure logic, no LLM call
    # ------------------------------------------------------------------ #

    def detect_gaps(
        self,
        concept_scores: dict[str, ConceptScore],
        question: QuestionMeta,
        triggered_misconceptions: Optional[list[str]] = None,
    ) -> list[Gap]:
        triggered_misconceptions = triggered_misconceptions or []
        gaps: list[Gap] = []
        core_concepts = question.core_concepts or question.expected_concepts

        for c in core_concepts:
            name, weight = c["name"], c.get("weight", 1.0)
            cs = concept_scores.get(name)
            status = cs.status if cs else ConceptStatus.ABSENT

            if status == ConceptStatus.ABSENT:
                gaps.append(Gap(concept=name, gap_type=GapType.MISSING, priority=weight * 1.0))
            elif status == ConceptStatus.PARTIAL:
                gaps.append(Gap(concept=name, gap_type=GapType.SHALLOW, priority=weight * 0.7))

            if name in triggered_misconceptions:
                gaps.append(Gap(concept=name, gap_type=GapType.MISCONCEIVED, priority=weight * 0.9))

        core_all_strong = bool(core_concepts) and all(
            concept_scores.get(
                c["name"], ConceptScore(concept=c["name"], status=ConceptStatus.ABSENT, score=0.0)
            ).status
            == ConceptStatus.STRONG
            for c in core_concepts
        )

        if core_all_strong:
            for c in question.nice_to_have:
                name, weight = c["name"], c.get("weight", 1.0)
                cs = concept_scores.get(name)
                if not cs or cs.status != ConceptStatus.STRONG:
                    gaps.append(Gap(concept=name, gap_type=GapType.MISSING, priority=weight * 0.4))

        gaps.sort(key=lambda g: g.priority, reverse=True)
        return gaps[:MAX_GAPS_PER_TURN]