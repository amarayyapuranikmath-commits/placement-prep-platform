from datetime import datetime, timezone
from typing import Any, ClassVar

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.models.user import PyObjectId

INTERVIEW_QUESTIONS_COLLECTION = "interview_questions"
INTERVIEW_SESSIONS_COLLECTION = "interview_sessions"
INTERVIEW_SESSION_ARCHIVES_COLLECTION = "interview_session_archives"


class InterviewQuestionModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    COLLECTION_NAME: ClassVar[str] = INTERVIEW_QUESTIONS_COLLECTION

    id: PyObjectId | None = Field(default=None, alias="_id")
    question_id: str
    interview_type: str
    category: str
    topic: str
    difficulty_rating: float = 1200.0
    difficulty: str
    role: str
    experience_level: str
    company_type: str
    question: str = Field(alias="question")
    expected_concepts: list[dict[str, Any]] = Field(default_factory=list)
    core_concepts: list[dict[str, Any]] = Field(default_factory=list)
    nice_to_have: list[dict[str, Any]] = Field(default_factory=list)
    common_misconceptions: list[dict[str, Any]] = Field(default_factory=list)
    attached_knowledge: dict[str, list[str]] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        return self.question
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


class InterviewSessionModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    COLLECTION_NAME: ClassVar[str] = INTERVIEW_SESSIONS_COLLECTION

    id: PyObjectId | None = Field(default=None, alias="_id")
    session_id: str
    candidate_id: str
    question_id: str
    persona: dict[str, Any] | None = None
    state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
