from datetime import datetime, timezone
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import PyObjectId

CODING_SUBMISSIONS_COLLECTION = "coding_submissions"

SUPPORTED_LANGUAGES = ["python", "java", "cpp", "javascript"]


class CodingSubmissionModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    COLLECTION_NAME: ClassVar[str] = CODING_SUBMISSIONS_COLLECTION

    id: PyObjectId | None = Field(default=None, alias="_id")

    # User & Problem
    user_id: str
    problem_id: str

    # Submission
    language: Literal["python", "java", "cpp", "javascript"]
    code: str

    # Judge0 Result
    status: str
    runtime_ms: float | None = None
    memory_kb: float | None = None

    passed_test_cases: int = 0
    total_test_cases: int = 0

    failed_case_index: int | None = None
    failed_test_number: int | None = None

    compile_error: str | None = None
    stderr: str | None = None

    # AI Feedback
    ai_feedback: dict[str, Any] | None = None

    # Timestamp
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )