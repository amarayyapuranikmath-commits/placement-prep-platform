"""
AIRE Quality Engine
====================
Implements:
    - SRL (#11) Self-Refinement Loop
    - RVL (#12) Response Verification Layer

Rule checks always run first (cheap, deterministic); the LLM is invoked
only to repair a flagged draft, capped at one retry, with a guaranteed
deterministic fallback so the pipeline can never emit a broken response.
"""

from __future__ import annotations

import re
import json
from typing import Optional

from . import (
    GroqClientProtocol,
    InterviewStateSnapshot,
    QuestionMeta,
    ResponseType,
    RetrievedChunk,
    StyleGuardrails,
    VerificationResult,
)
from .prompt_builder import PromptBuilder

MAX_REPAIR_RETRIES = 1
MAX_VERIFICATION_RETRIES = 1
OPENING_WORD_WINDOW = 3

FALLBACK_TEMPLATES = {
    ResponseType.QUESTION: "Let's take a step back — can you walk me through your reasoning on {concept} again?",
    ResponseType.FEEDBACK: "Let's move on to the next question.",
}


def _sentence_count(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+", text) if s.strip()])


def _opening_words(text: str, n: int = OPENING_WORD_WINDOW) -> str:
    return " ".join(text.strip().lower().split()[:n])


class QualityEngine:
    def __init__(self, groq_client: GroqClientProtocol, prompt_builder: Optional[PromptBuilder] = None) -> None:
        self._groq = groq_client
        self._prompts = prompt_builder or PromptBuilder()

    # ------------------------------------------------------------------ #
    # SRL (#11)
    # ------------------------------------------------------------------ #

    def rule_check(self, draft_text: str, guardrails: StyleGuardrails, recent_texts: list[str]) -> list[str]:
        issues = []
        if _sentence_count(draft_text) > guardrails.max_sentences:
            issues.append("too_long")

        lowered = draft_text.lower()
        if any(phrase in lowered for phrase in guardrails.banned_phrases):
            issues.append("banned_phrase")

        draft_opening = _opening_words(draft_text)
        if draft_opening and any(draft_opening == _opening_words(t) for t in recent_texts if t):
            issues.append("repetitive_opening")

        return issues

    async def refine(
        self,
        draft_text: str,
        guardrails: StyleGuardrails,
        recent_texts: list[str],
    ) -> tuple[str, bool]:
        issues = self.rule_check(draft_text, guardrails, recent_texts)
        if not issues:
            return draft_text, False

        current = draft_text
        for _ in range(MAX_REPAIR_RETRIES):
            messages = self._prompts.repair_prompt(current, issues, guardrails)
            repaired = (await self._groq.complete(messages, max_tokens=80, temperature=0.3)).strip()
            remaining = self.rule_check(repaired, guardrails, recent_texts)
            if not remaining:
                return repaired, True
            current = repaired
            issues = remaining

        return self._fallback_rewrite(draft_text, guardrails), True

    def _fallback_rewrite(self, draft_text: str, guardrails: StyleGuardrails) -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", draft_text) if s.strip()]
        trimmed = " ".join(sentences[: guardrails.max_sentences])
        for phrase in guardrails.banned_phrases:
            trimmed = re.sub(re.escape(phrase), "", trimmed, flags=re.IGNORECASE)
        return trimmed.strip() or "Let's continue."

    # ------------------------------------------------------------------ #
    # RVL (#12)
    # ------------------------------------------------------------------ #

    async def verify(
        self,
        refined_text: str,
        retrieved_chunks: list[RetrievedChunk],
        question: Optional[QuestionMeta],
        response_type: ResponseType,
        state: InterviewStateSnapshot,
        target_concept: Optional[str] = None,
    ) -> VerificationResult:
        reasons = self._gather_verification_reasons(refined_text, retrieved_chunks, question, response_type, state, target_concept)

        if not reasons:
            return VerificationResult(passed=True, final_text=refined_text)

        if state.verification_retry_count < MAX_VERIFICATION_RETRIES:
            state.verification_retry_count += 1
            messages = self._prompts.verification_repair_prompt(refined_text, reasons, response_type)
            regenerated = (await self._groq.complete(messages, max_tokens=100, temperature=0.3)).strip()
            return await self.verify(
                regenerated, retrieved_chunks, question, response_type, state, target_concept
            )

        fallback_text = FALLBACK_TEMPLATES[response_type].format(concept=target_concept or "this")
        return VerificationResult(passed=False, failure_reasons=reasons, final_text=fallback_text, used_fallback=True)

    async def refine_and_verify(
        self,
        draft_text: str,
        guardrails: StyleGuardrails,
        recent_texts: list[str],
        retrieved_chunks: list[RetrievedChunk],
        question: Optional[QuestionMeta],
        response_type: ResponseType,
        state: InterviewStateSnapshot,
        target_concept: Optional[str] = None,
    ) -> tuple[str, VerificationResult]:
        issues = self.rule_check(draft_text, guardrails, recent_texts)
        reasons = self._gather_verification_reasons(draft_text, retrieved_chunks, question, response_type, state, target_concept)

        if not issues and not reasons:
            return draft_text, VerificationResult(passed=True, final_text=draft_text)

        if not issues:
            verification_result = await self.verify(
                draft_text, retrieved_chunks, question, response_type, state, target_concept
            )
            return verification_result.final_text, verification_result

        if not reasons:
            refined_text, _ = await self.refine(draft_text, guardrails, recent_texts)
            verification_result = await self.verify(
                refined_text, retrieved_chunks, question, response_type, state, target_concept
            )
            return verification_result.final_text, verification_result

        if state.verification_retry_count < MAX_VERIFICATION_RETRIES:
            state.verification_retry_count += 1
            messages = self._prompts.repair_and_verify_prompt(
                draft_text,
                issues,
                reasons,
                guardrails,
                response_type,
            )
            regenerated = (await self._groq.complete(messages, max_tokens=100, temperature=0.3)).strip()
            return await self.verify(
                regenerated, retrieved_chunks, question, response_type, state, target_concept
            )

    async def batch_refine_and_verify(
        self,
        drafts: list[tuple[str, ResponseType]],
        guardrails: StyleGuardrails,
        recent_texts: list[str],
        retrieved_chunks: list[RetrievedChunk],
        question: Optional[QuestionMeta],
        state: InterviewStateSnapshot,
        target_concept: Optional[str] = None,
    ) -> list[tuple[str, VerificationResult]]:
        """Batch multiple (text, response_type) pairs into a single Groq call
        when both need repair/verification. Returns list of (final_text, VerificationResult)
        preserving the input order.
        """
        # Preliminary deterministic checks per draft
        needs_llm = []
        results: list[tuple[str, VerificationResult]] = []
        for idx, (text, rtype) in enumerate(drafts):
            issues = self.rule_check(text, guardrails, recent_texts)
            reasons = self._gather_verification_reasons(text, retrieved_chunks, question, rtype, state, target_concept)
            if not issues and not reasons:
                results.append((text, VerificationResult(passed=True, final_text=text)))
                needs_llm.append(None)
            else:
                results.append((None, None))
                needs_llm.append((idx, text, issues, reasons, rtype))

        # If nothing requires LLM, return early
        if all(n is None for n in needs_llm):
            return results

        # Build a single combined prompt containing only the items that need LLM,
        # including their original index so we can map results back deterministically.
        needs_idxs: list[int] = [n[0] for n in needs_llm if n is not None]
        payload = []
        for n in needs_llm:
            if n is None:
                continue
            _, text, issues, reasons, rtype = n
            payload.append({"idx": _, "text": text, "issues": issues, "reasons": reasons, "type": rtype.value})

        messages = [
            {"role": "system", "content": "You will be given a JSON array of items to repair+verify. For each item, return a JSON object with keys: idx, final_text, passed (true/false), failure_reasons (array). Return a JSON array of results in any order; idx links results to inputs."},
            {"role": "user", "content": json.dumps(payload)},
        ]

        raw = (await self._groq.complete(messages, max_tokens=400, temperature=0.3, json_mode=True)).strip()
        parsed = json.loads(raw) if raw else []

        # Map parsed results back to outputs, falling back to safe templates on failure
        for item in parsed:
            try:
                if isinstance(item, str):
                    # If the model returned a bare string, we can't know the idx; skip conservative mapping
                    continue
                orig_idx = int(item.get("idx"))
                draft_text, rtype = drafts[orig_idx]
                final = item.get("final_text")
                if final is None:
                    final = FALLBACK_TEMPLATES[rtype].format(concept=target_concept or "this")
                passed = bool(item.get("passed"))
                failure_reasons = item.get("failure_reasons", [])
                vr = VerificationResult(passed=passed, final_text=str(final), failure_reasons=failure_reasons)
            except Exception:
                # Conservative fallback: use deterministic fallback
                if not isinstance(item, dict) or "idx" not in item:
                    continue
                orig_idx = int(item.get("idx"))
                draft_text, rtype = drafts[orig_idx]
                fallback_text = FALLBACK_TEMPLATES[rtype].format(concept=target_concept or "this")
                vr = VerificationResult(passed=False, final_text=fallback_text, used_fallback=True)
            results[orig_idx] = (vr.final_text, vr)

        # Ensure any drafts not covered by LLM results get a conservative deterministic fallback
        for idx in range(len(results)):
            txt, vr = results[idx]
            if vr is None:
                draft_text, rtype = drafts[idx]
                fallback_text = FALLBACK_TEMPLATES[rtype].format(concept=target_concept or "this")
                results[idx] = (fallback_text, VerificationResult(passed=False, final_text=fallback_text, used_fallback=True))

        return results

    def _gather_verification_reasons(
        self,
        refined_text: str,
        retrieved_chunks: list[RetrievedChunk],
        question: Optional[QuestionMeta],
        response_type: ResponseType,
        state: InterviewStateSnapshot,
        target_concept: Optional[str] = None,
    ) -> list[str]:
        reasons: list[str] = []

        if response_type == ResponseType.FEEDBACK:
            claims = self._extract_factual_claims(refined_text)
            for claim in claims:
                if not self._grounded_in(claim, retrieved_chunks, question):
                    reasons.append(f"ungrounded_claim:{claim[:60]}")

        if response_type == ResponseType.QUESTION and target_concept:
            if target_concept.lower() not in refined_text.lower():
                reasons.append("missing_target_concept")

        if self._contradicts_prior_verdict(refined_text, state):
            reasons.append("contradiction")

        return reasons

    def _extract_factual_claims(self, text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 4]

    def _grounded_in(
        self, claim: str, retrieved_chunks: list[RetrievedChunk], question: Optional[QuestionMeta]
    ) -> bool:
        claim_lower = claim.lower()
        sources_text = " ".join(c.text.lower() for c in retrieved_chunks)
        if question:
            sources_text += " " + " ".join(m.get("name", "") for m in question.common_misconceptions).lower()
            sources_text += " " + " ".join(c.get("name", "") for c in question.expected_concepts).lower()

        key_terms = re.findall(r"[a-zA-Z]{4,}", claim_lower)
        if not key_terms:
            return True
        overlap = sum(1 for term in key_terms if term in sources_text)
        return (overlap / len(key_terms)) >= 0.3

    def _contradicts_prior_verdict(self, text: str, state: InterviewStateSnapshot) -> bool:
        if state.last_verdict is None:
            return False
        praising = any(w in text.lower() for w in ("great", "correct", "well done", "exactly right"))
        return praising and state.last_verdict.value in ("incorrect", "off_topic")