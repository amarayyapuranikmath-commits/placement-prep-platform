"""
AIRE Dialogue Engine
=====================
Implements:
    - FGE (#5) Follow-up Generation Engine
    - QDE (#8) Question Deduplication Engine
    - CSM (#9) Context State Machine (session-level state transitions)
    - FSE (#10) Feedback Synthesis Engine

The LLM (GroqClientProtocol) is used only for short, template-constrained
generations (follow-up wording, feedback callouts). Everything structural
(intent selection, template choice, state transitions, dedup thresholds,
pending-gap queueing) is rule-based.
"""

from __future__ import annotations

import re
from typing import Optional

from . import (
    AnswerObject,
    ConceptScore,
    ConceptStatus,
    CorrectnessVerdict,
    DuplicateCheckResult,
    EmbeddingProviderProtocol,
    FeedbackDraft,
    FollowUpDraft,
    FollowUpIntent,
    Gap,
    GapType,
    GroqClientProtocol,
    InterviewerPersona,
    InterviewPhase,
    InterviewStateSnapshot,
    Verdict,
)
from .prompt_builder import PromptBuilder

DUPLICATE_SIMILARITY_THRESHOLD = 0.87
CROSS_SESSION_SIMILARITY_THRESHOLD = 0.90
MAX_FOLLOWUP_RETRIES = 1
CORE_QUESTIONS_BEFORE_DEEP_DIVE = 3
WARMUP_TURN_LIMIT = 1


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _normalize_for_exact_match(text: str) -> str:
    stopwords = {"the", "a", "an", "is", "are", "of", "to", "in", "on", "for", "and"}
    words = re.findall(r"\w+", text.lower())
    return " ".join(w for w in words if w not in stopwords)


class DialogueEngine:
    OPENING_TAGS: dict[tuple[str, str], list[str]] = {
        (Verdict.CORRECT.value, "friendly"): ["Nice, that's right.", "Yep, exactly."],
        (Verdict.CORRECT.value, "balanced"): ["That's correct.", "Right, that tracks."],
        (Verdict.CORRECT.value, "strict"): ["Correct.", "That's accurate."],
        (Verdict.PARTIALLY_CORRECT.value, "friendly"): ["You're partly there.", "Good start on that."],
        (Verdict.PARTIALLY_CORRECT.value, "balanced"): ["That's on the right track.", "Partially, yes."],
        (Verdict.PARTIALLY_CORRECT.value, "strict"): ["That's incomplete.", "Not fully there yet."],
        (Verdict.INCORRECT.value, "friendly"): ["Not quite, let's look at it differently.", "Close, but not quite."],
        (Verdict.INCORRECT.value, "balanced"): ["That's not quite right.", "I'd push back on that."],
        (Verdict.INCORRECT.value, "strict"): ["That's incorrect.", "That doesn't hold up."],
        (Verdict.OFF_TOPIC.value, "friendly"): ["Let's back up a bit.", "Let me clarify the question."],
        (Verdict.OFF_TOPIC.value, "balanced"): ["Let's refocus on the question.", "That's a bit off-topic."],
        (Verdict.OFF_TOPIC.value, "strict"): ["That doesn't address the question.", "Let's refocus."],
    }

    def __init__(
        self,
        groq_client: GroqClientProtocol,
        embedding_provider: EmbeddingProviderProtocol,
        prompt_builder: Optional[PromptBuilder] = None,
    ) -> None:
        self._groq = groq_client
        self._embed = embedding_provider
        self._prompts = prompt_builder or PromptBuilder()

    # ------------------------------------------------------------------ #
    # FGE (#5)
    # ------------------------------------------------------------------ #

    async def generate_followup(
        self,
        target_gap: Optional[Gap],
        state: InterviewStateSnapshot,
        candidate_last_claim_text: str = "",
        asked_question_embeddings: Optional[list[list[float]]] = None,
    ) -> Optional[FollowUpDraft]:
        """
        `target_gap` should be the gap already selected by CSM.advance_state
        (which owns pending-gap queueing). If None, the caller should advance
        to the next main question instead of forcing a follow-up.
        """
        if target_gap is None:
            return None

        intent_map = {
            GapType.MISSING: FollowUpIntent.PROBE,
            GapType.SHALLOW: FollowUpIntent.EXTEND,
            GapType.MISCONCEIVED: FollowUpIntent.CORRECT,
        }
        intent = intent_map[target_gap.gap_type]

        # Request two compact variations in one Groq call to avoid retrying.
        base_messages = self._prompts.followup_prompt(
            intent=intent,
            concept=target_gap.concept,
            candidate_claim=candidate_last_claim_text,
            persona=state.persona,
        )
        # Ask the model to return two distinct phrasings separated by a known delimiter.
        delim = "|||"
        prompt_note = {
            "role": "user",
            "content": (
                f"Please provide TWO distinct phrasings of the requested follow-up, "
                f"each one short. Separate the two phrasings with the delimiter {delim} and output only the phrasings."
            ),
        }
        messages = base_messages + [prompt_note]
        raw = await self._groq.complete(messages, max_tokens=120, temperature=0.6)
        parts = [p.strip() for p in raw.split(delim) if p.strip()]

        # Fallback: if model didn't follow delimiter, treat whole raw as single candidate.
        candidates = parts or [raw.strip()]

        # Pick first non-duplicate candidate; fall back to first candidate.
        for cand in candidates:
            dup_check = await self.is_duplicate(cand, state, asked_question_embeddings)
            if not dup_check.is_duplicate:
                return FollowUpDraft(text=cand, targets_gap=target_gap.concept, intent=intent)

        return FollowUpDraft(text=candidates[0], targets_gap=target_gap.concept, intent=intent)

    # ------------------------------------------------------------------ #
    # QDE (#8)
    # ------------------------------------------------------------------ #

    async def is_duplicate(
        self,
        draft_text: str,
        state: InterviewStateSnapshot,
        asked_question_embeddings: Optional[list[list[float]]] = None,
        cross_session: bool = False,
    ) -> DuplicateCheckResult:
        normalized = _normalize_for_exact_match(draft_text)
        existing_normalized = {_normalize_for_exact_match(q) for q in state.asked_question_texts}
        if normalized in existing_normalized:
            return DuplicateCheckResult(is_duplicate=True, similarity=1.0)

        if not state.asked_question_texts:
            return DuplicateCheckResult(is_duplicate=False, similarity=0.0)

        draft_embedding = await self._embed.embed(draft_text)
        cached_embeddings = asked_question_embeddings
        if cached_embeddings is None:
            # Fallback: recompute. Production callers should pass a cached
            # embedding list (e.g. from a Redis-backed session cache) to
            # avoid re-embedding every prior question on every check.
            cached_embeddings = await self._embed.embed_batch(state.asked_question_texts)

        threshold = CROSS_SESSION_SIMILARITY_THRESHOLD if cross_session else DUPLICATE_SIMILARITY_THRESHOLD
        best_score, best_idx = 0.0, -1
        for idx, emb in enumerate(cached_embeddings):
            sim = _cosine_similarity(draft_embedding, emb)
            if sim > best_score:
                best_score, best_idx = sim, idx

        if best_score >= threshold:
            match_id = (
                state.asked_question_texts[best_idx] if 0 <= best_idx < len(state.asked_question_texts) else None
            )
            return DuplicateCheckResult(is_duplicate=True, similarity=best_score, closest_match_id=match_id)

        return DuplicateCheckResult(is_duplicate=False, similarity=best_score)

    # ------------------------------------------------------------------ #
    # CSM (#9)
    # ------------------------------------------------------------------ #

    def advance_state(
        self,
        state: InterviewStateSnapshot,
        answer: AnswerObject,
        verdict: CorrectnessVerdict,
        gap_list: list[Gap],
    ) -> tuple[InterviewStateSnapshot, Optional[Gap]]:
        state.turn_index += 1
        state.covered_concepts |= answer.mentioned_concepts
        state.last_verdict = verdict.verdict
        state.recent_off_topic_count = (
            state.recent_off_topic_count + 1 if verdict.verdict == Verdict.OFF_TOPIC else 0
        )

        if state.pending_gaps:
            next_target: Optional[Gap] = state.pending_gaps.pop(0)
        elif gap_list:
            next_target = gap_list[0]
            if len(gap_list) > 1:
                state.pending_gaps.extend(gap_list[1:])
        else:
            next_target = None

        state.phase = self._compute_phase(state.turn_index, state.phase)
        return state, next_target

    def _compute_phase(self, turn_index: int, current_phase: InterviewPhase) -> InterviewPhase:
        if turn_index <= WARMUP_TURN_LIMIT:
            return InterviewPhase.WARMUP
        if current_phase == InterviewPhase.WARMUP:
            return InterviewPhase.CORE
        if current_phase == InterviewPhase.CORE and turn_index >= CORE_QUESTIONS_BEFORE_DEEP_DIVE:
            return InterviewPhase.DEEP_DIVE
        return current_phase

    def enter_wrap_up(self, state: InterviewStateSnapshot) -> InterviewStateSnapshot:
        state.phase = InterviewPhase.WRAP_UP
        return state

    # ------------------------------------------------------------------ #
    # FSE (#10)
    # ------------------------------------------------------------------ #

    async def generate_feedback(
        self,
        verdict: CorrectnessVerdict,
        concept_scores: dict[str, ConceptScore],
        gap_list: list[Gap],
        persona: InterviewerPersona,
    ) -> FeedbackDraft:
        opening_options = self.OPENING_TAGS.get((verdict.verdict.value, persona.strictness), ["Okay."])
        opening = opening_options[0]

        strong_concepts = [name for name, cs in concept_scores.items() if cs.status == ConceptStatus.STRONG]
        referenced: list[str] = []
        positive_point = ""
        if strong_concepts:
            referenced.append(strong_concepts[0])
            positive_point = await self._callout(strong_concepts[0], persona)

        gap_point = ""
        if gap_list:
            referenced.append(gap_list[0].concept)
            gap_point = self._describe_gap(gap_list[0])

        parts = [p for p in (opening, positive_point, gap_point) if p]
        text = " ".join(parts[:3])
        return FeedbackDraft(text=text, opening_tag=opening, referenced_concepts=referenced)

    async def _callout(self, concept: str, persona: InterviewerPersona) -> str:
        # Use a deterministic short template for most personas to avoid an LLM call.
        if persona.strictness in ("friendly", "balanced"):
            return f"You handled {concept} correctly."

        # For strict persona, keep the short LLM-generated callout for tone.
        messages = self._prompts.positive_callout_prompt(concept, persona)
        text = await self._groq.complete(messages, max_tokens=40, temperature=0.5)
        return text.strip()

    def _describe_gap(self, gap: Gap) -> str:
        templates = {
            GapType.MISSING: f"You didn't touch on {gap.concept} though.",
            GapType.SHALLOW: f"You named {gap.concept} but didn't explain why it matters.",
            GapType.MISCONCEIVED: f"I'd double check your understanding of {gap.concept}.",
        }
        return templates[gap.gap_type]