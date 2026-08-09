from datetime import datetime, timezone
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import PyObjectId

CODING_PROBLEMS_COLLECTION = "coding_problems"

SUPPORTED_LANGUAGES = ["python", "java", "cpp", "javascript"]
DIFFICULTIES = ["easy", "medium", "hard"]


class TestCase(BaseModel):
    input: str
    expected_output: str


class CodingProblemModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    COLLECTION_NAME: ClassVar[str] = CODING_PROBLEMS_COLLECTION

    id: PyObjectId | None = Field(default=None, alias="_id")

    title: str

    # Optional metadata only. Never use for routing or database lookups.
    slug: str | None = None

    category: str

    difficulty: Literal["easy", "medium", "hard"]

    tags: list[str] = Field(default_factory=list)

    statement: str

    input_format: str

    output_format: str

    constraints: str

    examples: list[TestCase] = Field(default_factory=list)

    visible_test_cases: list[TestCase] = Field(default_factory=list)

    hidden_test_cases: list[TestCase] = Field(default_factory=list)

    # Language -> Starter Code
    starter_code: dict[str, str] = Field(default_factory=dict)

    # Judge0 execution limits
    time_limit_ms: int = 1000
    memory_limit_mb: int = 128

    # Statistics
    total_submissions: int = 0
    total_accepted: int = 0

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )