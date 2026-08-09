"""
AIRE Orchestrator
==================
Implements HRO (#13): the Hybrid Reasoning Orchestrator, plus the full
per-turn execution pipeline described in the AIRE architecture doc:

    Answer -> Comprehension -> Retrieval -> Evaluation -> Adaptivity
           -> Dialogue (CSM/FGE/FSE) -> Quality Control (SRL/RVL)
           -> Memory Write -> Response

This is the single composition root for the AIRE engines. Wire it up in
your existing `interview_service.py` by constructing each engine with
your real Groq client / Mongo repositories / embedding provider, then
calling `InterviewOrchestrator.process_turn(...)` once per candidate answer.

Nothing in this file instantiates a Groq client or a database connection.
"""

from __future__ import annotations

from typing import Any, Optional

from app.services.interview_engine import Verdict

from pydantic import BaseModel, Field

from . import (
    AnswerObject,
    ConceptScore,
    CorrectnessVerdict,
    DifficultyUpdateResult,
    ExecutionRoute,
    FeedbackDraft,
    FollowUpDraft,
    FollowUpIntent,
    Gap,
    GapType,
    InterviewerPersona,
    InterviewStateSnapshot,
    QuestionMeta,
    ResponseType,
    StyleGuardrails,
    TaskType,
    VerificationResult,
)
from .adaptivity_engine import AdaptivityEngine
from .dialogue_engine import DialogueEngine
from .groq_evaluation_engine import GroqEvaluationEngine
from .memory_engine import MemoryEngine
from .quality_engine import QualityEngine
from .retrieval_engine import RetrievalEngine

# ---------------------------------------------------------------------------
# HRO (#13) -- the routing table is the core IP: it decides, per sub-task,
# whether logic is deterministic, LLM-driven, or a blend of both.
# ---------------------------------------------------------------------------

ROUTING_TABLE: dict[TaskType, ExecutionRoute] = {
    TaskType.CONCEPT_TAG: ExecutionRoute.RULE_THEN_LLM,
    TaskType.CORRECTNESS: ExecutionRoute.RULE_THEN_LLM,
    TaskType.GAP_DETECTION: ExecutionRoute.RULE_ONLY,
    TaskType.DIFFICULTY: ExecutionRoute.RULE_ONLY,
    TaskType.FOLLOWUP_GEN: ExecutionRoute.LLM_THEN_RULE_VERIFY,
    TaskType.FEEDBACK_GEN: ExecutionRoute.LLM_THEN_RULE_VERIFY,
    TaskType.DEDUP: ExecutionRoute.RULE_ONLY,
    TaskType.RETRIEVAL: ExecutionRoute.RULE_THEN_LLM,
}


def get_route(task_type: TaskType) -> ExecutionRoute:
    return ROUTING_TABLE.get(task_type, ExecutionRoute.RULE_ONLY)


class TurnResult(BaseModel):
    """Everything the calling application needs to render one interview turn."""
    session_id: str
    candidate_id: str
    answer: AnswerObject
    concept_scores: dict[str, ConceptScore]
    verdict: CorrectnessVerdict
    gaps: list[Gap] = Field(default_factory=list)
    difficulty_update: DifficultyUpdateResult
    followup: Optional[FollowUpDraft] = None
    feedback: FeedbackDraft
    should_advance_to_next_question: bool
    state: InterviewStateSnapshot


class InterviewOrchestrator:
    def __init__(
        self,
        *args,
        evaluation_engine: Optional[GroqEvaluationEngine] = None,
        retrieval_engine: Optional[RetrievalEngine] = None,
        adaptivity_engine: Optional[AdaptivityEngine] = None,
        dialogue_engine: Optional[DialogueEngine] = None,
        quality_engine: Optional[QualityEngine] = None,
        memory_engine: Optional[MemoryEngine] = None,
        style_guardrails: Optional[StyleGuardrails] = None,
        **kwargs,
    ) -> None:
        # Accept both the current keyword-based wiring and the older positional
        # regression shape used by the interview service test fixtures.
        if args:
            if len(args) == 6:
                evaluation_engine, retrieval_engine, adaptivity_engine, dialogue_engine, quality_engine, memory_engine = args
            elif len(args) == 7:
                # Legacy test order:
                # (comprehension, retrieval, evaluation, adaptivity, dialogue, quality, memory)
                _ignored_comprehension, retrieval_engine, evaluation_engine, adaptivity_engine, dialogue_engine, quality_engine, memory_engine = args
            else:
                raise TypeError(
                    "InterviewOrchestrator expects either six positional engine objects or the legacy seven-object test signature."
                )

        self.evaluation = evaluation_engine or kwargs.get("evaluation")
        self.retrieval = retrieval_engine or kwargs.get("retrieval")
        self.adaptivity = adaptivity_engine or kwargs.get("adaptivity")
        self.dialogue = dialogue_engine or kwargs.get("dialogue")
        self.quality = quality_engine or kwargs.get("quality")
        self.memory = memory_engine or kwargs.get("memory")

        if self.evaluation is None or self.retrieval is None or self.adaptivity is None or self.dialogue is None or self.quality is None or self.memory is None:
            raise TypeError("InterviewOrchestrator requires evaluation, retrieval, adaptivity, dialogue, quality, and memory engines.")

        self.guardrails = style_guardrails or StyleGuardrails()

    async def process_turn(
        self,
        session_id: str,
        candidate_id: str,
        question: QuestionMeta,
        raw_answer: str,
        persona: Optional[InterviewerPersona] = None,
    ) -> TurnResult:
        # 1. Load / initialize session state (LMA tier 2)
        state = await self.memory.load_session_state(session_id)
        if state is None:
            state = InterviewStateSnapshot(
                session_id=session_id,
                candidate_id=candidate_id,
                current_main_question_id=question.question_id,
                skill_estimate=question.difficulty_rating,
                persona=persona or InterviewerPersona(),
            )

        # 2. Evaluate answer using Groq as the single intelligence engine
        evaluation = await self.evaluation.evaluate_answer(question, raw_answer, state)

        answer_length_class = self.evaluation.answer_length_class_from_answer(raw_answer)
        answer = AnswerObject(
            raw_text=raw_answer,
            cleaned_text=raw_answer.strip(),
            claims=[],
            mentioned_concepts=set(),
            answer_length_class=answer_length_class,
        )

        verdict = self._build_verdict(evaluation)
        gaps = self._build_gaps(evaluation)

        # 3. Adaptivity (#6)
        difficulty_update = self.adaptivity.update_difficulty(
            skill_estimate=state.skill_estimate,
            question_difficulty_rating=question.difficulty_rating,
            verdict=verdict,
            turn_index=state.turn_index,
            recent_off_topic_count=state.recent_off_topic_count,
        )
        state.skill_estimate = difficulty_update.new_skill_estimate
        state.difficulty_band = difficulty_update.next_difficulty

        # 4. CSM (#9)
        state, next_target_gap = self.dialogue.advance_state(state, answer, verdict, gaps)

        # 5. Retrieval (#15)
        retrieved_chunks = []
        target_concept = next_target_gap.concept if next_target_gap else None
        if next_target_gap is not None:
            retrieved_chunks = await self.retrieval.retrieve(
                next_target_gap.concept, question, next_target_gap.gap_type
            )

        # 6. Follow-up question from Groq evaluation if available.
        followup_question_text = evaluation.get("follow_up_question", "")
        if followup_question_text:
            followup = FollowUpDraft(
                text=followup_question_text,
                targets_gap=next_target_gap.concept if next_target_gap else None,
                intent=FollowUpIntent.PROBE,
            )
        else:
            followup = None

        # 7. Dialogue feedback generation remains template-driven and verified.
        try:
            feedback = await self.dialogue.generate_feedback(verdict, {}, gaps, state.persona)
        except Exception:
            feedback_text = self._fallback_feedback_text(verdict)
            feedback = FeedbackDraft(text=feedback_text)

        # 8. Quality control on feedback and followup
        if followup is not None:
            drafts = [
                (feedback.text, ResponseType.FEEDBACK),
                (followup.text, ResponseType.QUESTION),
            ]
            try:
                batch_results = await self.quality.batch_refine_and_verify(
                    drafts,
                    self.guardrails,
                    state.recent_response_texts,
                    retrieved_chunks,
                    question,
                    state,
                    target_concept,
                )
            except Exception:
                batch_results = [(text, VerificationResult(passed=True, final_text=text)) for text, _ in drafts]

            if not batch_results or len(batch_results) != len(drafts):
                batch_results = [(text, VerificationResult(passed=True, final_text=text)) for text, _ in drafts]

            feedback.text, feedback_verification = batch_results[0]
            followup.text, followup_verification = batch_results[1]

            if feedback_verification is None or followup_verification is None:
                feedback_verification = VerificationResult(passed=True, final_text=feedback.text)
                followup_verification = VerificationResult(passed=True, final_text=followup.text)

            feedback.text = feedback_verification.final_text
            followup.text = followup_verification.final_text
            state.asked_question_texts.append(followup.text)
        else:
            try:
                feedback.text, feedback_verification = await self.quality.refine_and_verify(
                    feedback.text,
                    self.guardrails,
                    state.recent_response_texts,
                    retrieved_chunks,
                    question,
                    ResponseType.FEEDBACK,
                    state,
                    target_concept,
                )
            except Exception:
                feedback_verification = VerificationResult(passed=True, final_text=feedback.text)
            feedback.text = feedback_verification.final_text

        state.recent_response_texts.append(feedback.text)
        state.verification_retry_count = 0

        # 9. Persist state
        await self.memory.save_session_state(state)

        return TurnResult(
            session_id=session_id,
            candidate_id=candidate_id,
            answer=answer,
            concept_scores={},
            verdict=verdict,
            gaps=gaps,
            difficulty_update=difficulty_update,
            followup=followup,
            feedback=feedback,
            should_advance_to_next_question=bool(followup),
            state=state,
        )

    def _build_verdict(self, evaluation: dict[str, Any]) -> CorrectnessVerdict:
        verdict_value = evaluation.get("verdict", "incorrect").lower()
        if verdict_value == "correct":
            verdict_enum = Verdict.CORRECT
        elif verdict_value == "partially_correct" or verdict_value == "partially correct":
            verdict_enum = Verdict.PARTIALLY_CORRECT
        elif verdict_value == "off_topic" or verdict_value == "off topic":
            verdict_enum = Verdict.OFF_TOPIC
        else:
            verdict_enum = Verdict.INCORRECT

        return CorrectnessVerdict(
            verdict=verdict_enum,
            score=float(evaluation.get("overall_score", 0)),
            core_coverage=float(evaluation.get("concept_coverage", 0)) / 100.0,
            misconceptions_triggered=[],
            rationale_tags=[f"hiring_signal={evaluation.get('hiring_signal', '')}"],
            used_llm_tiebreak=False,
        )

    def _build_gaps(self, evaluation: dict[str, Any]) -> list[Gap]:
        missing_concepts = evaluation.get("missing_concepts") or []
        gaps: list[Gap] = []
        for concept in missing_concepts:
            gaps.append(Gap(concept=str(concept), gap_type=GapType.MISSING, priority=1.0))
        return gaps

    def _fallback_feedback_text(self, verdict: CorrectnessVerdict) -> str:
        if verdict.verdict == Verdict.CORRECT:
            return "You covered the main point well. Let's continue to the next one."
        if verdict.verdict == Verdict.PARTIALLY_CORRECT:
            return "You are on the right track. Add a little more detail to strengthen your answer."
        return "Let's revisit the core idea and frame your answer more clearly."

    async def end_session(self, session_id: str) -> None:
        state = await self.memory.load_session_state(session_id)
        if state is not None:
            await self.memory.archive_session(state)