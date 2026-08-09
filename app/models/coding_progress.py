from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

CODING_PROGRESS_COLLECTION = "coding_progress"


class CodingProgressModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    COLLECTION_NAME: ClassVar[str] = CODING_PROGRESS_COLLECTION

    # User
    user_id: str

    # Solved Problems
    solved_problem_ids: list[str] = Field(default_factory=list)

    total_solved: int = 0

    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0

    # Progress Tracking
    current_streak: int = 0
    longest_streak: int = 0

    total_submissions: int = 0
    total_accepted: int = 0

    acceptance_rate: float = 0.0

    # Last Activity
    last_solved_at: datetime | None = None

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )