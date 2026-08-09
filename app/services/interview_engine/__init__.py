"""
AIRE - Adaptive Interview Reasoning Engine
============================================
Core shared types, enums, and dependency interfaces (Protocols) used across
all AIRE engine modules.

This package deliberately contains NO concrete MongoDB / Groq client code.
Every external dependency (LLM calls, database reads/writes, embeddings,
question-bank lookups) is expressed here as a `typing.Protocol` so the
existing application code can supply real implementations via dependency
injection, without this package importing or instantiating them directly.

Engines in this package:
    comprehension_engine  -> SAD (#1) + CCG (#2)
    retrieval_engine       -> RE  (#15)
    evaluation_engine      -> CSE (#3) + GDM (#4)
    adaptivity_engine      -> ADC (#6)
    dialogue_engine        -> FGE (#5) + QDE (#8) + CSM (#9) + FSE (#10)
    quality_engine         -> SRL (#11) + RVL (#12)
    prompt_builder         -> prompt/template construction (no LLM calls)
    memory_engine          -> LTM (#7) + LMA (#14)
    orchestrator           -> HRO (#13) + full turn pipeline
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ConceptStatus(str, Enum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"
    ABSENT = "absent"


class ReasoningType(str, Enum):
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    COMPARISON = "comparison"
    TRADEOFF = "tradeoff"
    CODE = "code"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class AnswerLengthClass(str, Enum):
    TOO_SHORT = "too_short"
    ADEQUATE = "adequate"
    VERBOSE = "verbose"


class Verdict(str, Enum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    OFF_TOPIC = "off_topic"


class GapType(str, Enum):
    MISSING = "missing"
    SHALLOW = "shallow"
    MISCONCEIVED = "misconceived"


class FollowUpIntent(str, Enum):
    PROBE = "probe"
    EXTEND = "extend"
    CORRECT = "correct"
    CLARIFY = "clarify"


class DifficultyBand(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class InterviewPhase(str, Enum):
    WARMUP = "warmup"
    CORE = "core"
    DEEP_DIVE = "deep_dive"
    WRAP_UP = "wrap_up"


class ExecutionRoute(str, Enum):
    RULE_ONLY = "rule_only"
    LLM_ONLY = "llm_only"
    RULE_THEN_LLM = "rule_then_llm"
    LLM_THEN_RULE_VERIFY = "llm_then_rule_verify"


class ResponseType(str, Enum):
    QUESTION = "question"
    FEEDBACK = "feedback"


class TaskType(str, Enum):
    CONCEPT_TAG = "concept_tag"
    CORRECTNESS = "correctness"
    GAP_DETECTION = "gap_detection"
    DIFFICULTY = "difficulty"
    FOLLOWUP_GEN = "followup_gen"
    FEEDBACK_GEN = "feedback_gen"
    DEDUP = "dedup"
    RETRIEVAL = "retrieval"


# ---------------------------------------------------------------------------
# Core data models  (pydantic v2, project-wide convention)
# ---------------------------------------------------------------------------

class Claim(BaseModel):
    id: str
    text: str
    concepts: list[str] = Field(default_factory=list)
    confidence: str = "medium"  # "high" (dictionary match) | "medium" (llm-tagged)
    hedge_score: float = 0.0


class AnswerObject(BaseModel):
    """Output of the Comprehension Engine's SAD algorithm (#1)."""
    raw_text: str
    cleaned_text: str
    claims: list[Claim] = Field(default_factory=list)
    mentioned_concepts: set[str] = Field(default_factory=set)
    code_present: bool = False
    code_blocks: list[str] = Field(default_factory=list)
    reasoning_type: ReasoningType = ReasoningType.UNKNOWN
    hedge_score: float = 0.0
    filler_ratio: float = 0.0
    answer_length_class: AnswerLengthClass = AnswerLengthClass.ADEQUATE


class ConceptScore(BaseModel):
    """Single entry in the ConceptScoreMap produced by CCG (#2)."""
    concept: str
    status: ConceptStatus
    score: float
    evidence_claim_ids: list[str] = Field(default_factory=list)


class CorrectnessVerdict(BaseModel):
    """Output of CSE (#3)."""
    verdict: Verdict
    score: float
    core_coverage: float
    misconceptions_triggered: list[str] = Field(default_factory=list)
    rationale_tags: list[str] = Field(default_factory=list)
    used_llm_tiebreak: bool = False


class Gap(BaseModel):
    """Single entry in the GapList produced by GDM (#4)."""
    concept: str
    gap_type: GapType
    priority: float


class FollowUpDraft(BaseModel):
    """Output of FGE (#5)."""
    text: str
    targets_gap: Optional[str] = None
    intent: FollowUpIntent = FollowUpIntent.PROBE


class FeedbackDraft(BaseModel):
    """Output of FSE (#10)."""
    text: str
    opening_tag: str = ""
    referenced_concepts: list[str] = Field(default_factory=list)


class RetrievedChunk(BaseModel):
    """Output of RE (#15)."""
    text: str
    source_id: str
    relevance_score: float = 0.0
    is_core: bool = False


class DifficultyUpdateResult(BaseModel):
    """Output of ADC (#6)."""
    new_skill_estimate: float
    next_difficulty: DifficultyBand
    reason: str


class DuplicateCheckResult(BaseModel):
    """Output of QDE (#8)."""
    is_duplicate: bool
    similarity: float = 0.0
    closest_match_id: Optional[str] = None


class VerificationResult(BaseModel):
    """Output of RVL (#12)."""
    passed: bool
    failure_reasons: list[str] = Field(default_factory=list)
    final_text: str
    used_fallback: bool = False


class InterviewerPersona(BaseModel):
    tone: str = "neutral"
    strictness: str = "balanced"  # "friendly" | "balanced" | "strict"


class QuestionMeta(BaseModel):
    """
    Rubric/content describing a single interview-bank question.
    This is a read-only view into your existing question-bank data;
    populate it from your real question documents when calling these engines.
    """
    model_config = ConfigDict(populate_by_name=True)

    question_id: str
    interview_type: str = "technical"
    category: str = ""
    topic: str
    difficulty: str = "medium"
    difficulty_rating: float = 1200.0
    role: str = "Any"
    experience_level: str = "Any"
    company_type: str = "any"
    text: str = Field(alias="question")

    expected_concepts: list[dict[str, Any]] = Field(default_factory=list)  # [{name, weight, is_core}]
    core_concepts: list[dict[str, Any]] = Field(default_factory=list)
    nice_to_have: list[dict[str, Any]] = Field(default_factory=list)
    common_misconceptions: list[dict[str, Any]] = Field(default_factory=list)  # [{name, pattern}]
    attached_knowledge: dict[str, list[str]] = Field(default_factory=dict)  # concept -> [chunks]

    keywords: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    ideal_answer_summary: str = ""
    evaluation_hints: list[str] = Field(default_factory=list)
    estimated_answer_time: int = 0
    estimated_score: int = 0
    tags: list[str] = Field(default_factory=list)
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterviewStateSnapshot(BaseModel):
    """
    Lightweight, engine-facing view of interview session state (CSM, #9).
    This is NOT the persisted DB document/model for a session -- it is the
    structured object AIRE engines read and update each turn. Your existing
    `interview_service.py` / DB models own the actual persistence schema;
    load/save this snapshot via `SessionRepositoryProtocol`.
    """
    session_id: str
    candidate_id: str
    phase: InterviewPhase = InterviewPhase.WARMUP
    current_main_question_id: Optional[str] = None
    pending_gaps: list[Gap] = Field(default_factory=list)
    turn_index: int = 0
    skill_estimate: float = 1200.0
    difficulty_band: DifficultyBand = DifficultyBand.MEDIUM
    covered_concepts: set[str] = Field(default_factory=set)
    asked_question_texts: list[str] = Field(default_factory=list)
    recent_response_texts: list[str] = Field(default_factory=list)
    persona: InterviewerPersona = Field(default_factory=InterviewerPersona)
    verification_retry_count: int = 0
    recent_off_topic_count: int = 0
    last_verdict: Optional[Verdict] = None


class StyleGuardrails(BaseModel):
    max_sentences: int = 3
    banned_phrases: list[str] = Field(default_factory=lambda: [
        "great job", "that's correct", "as an ai", "as an ai language model",
        "i'm just an ai", "well done!", "perfect answer",
    ])


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Dependency interfaces (Protocols) -- implement these against YOUR existing
# Groq client, MongoDB (Motor) collections, embedding model, etc.
# Nothing in this package instantiates a concrete client/connection.
# ---------------------------------------------------------------------------

@runtime_checkable
class GroqClientProtocol(Protocol):
    """
    Wrap your EXISTING Groq client behind this interface. Do not create a
    new Groq client inside the interview_engine package -- inject an
    adapter around your current client that satisfies this Protocol.
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 256,
        temperature: float = 0.4,
        json_mode: bool = False,
    ) -> str:
        """Return the model's raw text (or JSON string if json_mode=True)."""
        ...


@runtime_checkable
class EmbeddingProviderProtocol(Protocol):
    """Wrap your existing embedding model/service."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


@runtime_checkable
class CandidateProfileRepositoryProtocol(Protocol):
    """
    Wrap your existing MongoDB `candidate_profiles` collection access
    (Motor). Expected document shape (informational only):
        { candidate_id, concept_mastery: {concept: {ema_score, last_seen,
          times_tested, weak_streak}}, session_count, last_active }
    """

    @abstractmethod
    async def get_profile(self, candidate_id: str) -> dict[str, Any]: ...

    @abstractmethod
    async def save_profile(self, candidate_id: str, profile: dict[str, Any]) -> None: ...


@runtime_checkable
class SessionRepositoryProtocol(Protocol):
    """Wrap your existing MongoDB `interview_sessions` collection access."""

    @abstractmethod
    async def get_state(self, session_id: str) -> Optional[dict[str, Any]]: ...

    @abstractmethod
    async def save_state(self, session_id: str, state: dict[str, Any]) -> None: ...

    @abstractmethod
    async def get_history(self, candidate_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def archive_state(self, session_id: str, summary: dict[str, Any]) -> None: ...

    @abstractmethod
    async def delete_state(self, session_id: str) -> None: ...


@runtime_checkable
class KnowledgeBaseRepositoryProtocol(Protocol):
    """
    Wrap your existing curated knowledge base / vector index
    (e.g. MongoDB Atlas Vector Search) for the RE fallback path (#15).
    """

    @abstractmethod
    async def vector_search(
        self, query_vector: list[float], top_k: int = 10
    ) -> list[RetrievedChunk]: ...


@runtime_checkable
class QuestionBankRepositoryProtocol(Protocol):
    """Wrap your existing question-bank storage."""

    @abstractmethod
    async def get_question(self, question_id: str) -> QuestionMeta: ...

    @abstractmethod
    async def select_question(self, config: dict[str, Any]) -> QuestionMeta: ...


__all__ = [
    # enums
    "ConceptStatus", "ReasoningType", "AnswerLengthClass", "Verdict", "GapType",
    "FollowUpIntent", "DifficultyBand", "InterviewPhase", "ExecutionRoute",
    "ResponseType", "TaskType",
    # models
    "Claim", "AnswerObject", "ConceptScore", "CorrectnessVerdict", "Gap",
    "FollowUpDraft", "FeedbackDraft", "RetrievedChunk", "DifficultyUpdateResult",
    "DuplicateCheckResult", "VerificationResult", "InterviewerPersona",
    "QuestionMeta", "InterviewStateSnapshot", "StyleGuardrails",
    # protocols
    "GroqClientProtocol", "EmbeddingProviderProtocol",
    "CandidateProfileRepositoryProtocol", "SessionRepositoryProtocol",
    "KnowledgeBaseRepositoryProtocol", "QuestionBankRepositoryProtocol",
    # utils
    "utcnow",
]