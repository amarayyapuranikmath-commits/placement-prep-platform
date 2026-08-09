from datetime import datetime, timezone
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

APTITUDE_QUESTION_COLLECTION = "aptitude_questions"


class AptitudeQuestionModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    COLLECTION_NAME: ClassVar[str] = APTITUDE_QUESTION_COLLECTION

    id: Any | None = Field(default=None, alias="_id")
    question_id: str
    category: str
    topic: str
    difficulty: str
    question: str
    options: list[str] = Field(default_factory=list)
    correct_answer: str
    explanation: str
    company_tags: list[str] = Field(default_factory=list)
    estimated_time: int = 0
    marks: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
