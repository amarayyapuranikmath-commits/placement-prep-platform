from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

SUPPORTED_LANGUAGES = ["python", "java", "cpp", "javascript"]


def _validate_language(value: str) -> str:
    if value not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Language must be one of {SUPPORTED_LANGUAGES}")
    return value


# ==========================================================
# Coding Preferences
# ==========================================================

class PreferenceUpdateRequest(BaseModel):
    preferred_language: Literal["python", "java", "cpp", "javascript"]

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return _validate_language(value)


class PreferenceResponse(BaseModel):
    preferred_language: str | None = None


# ==========================================================
# Problems
# ==========================================================

class TestCaseSchema(BaseModel):
    input: str
    expected_output: str


class ProblemSummaryResponse(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)
    is_solved: bool
    acceptance_rate: float = 0.0


class ProblemListResponse(BaseModel):
    problems: list[ProblemSummaryResponse]
    total: int
    page: int
    page_size: int


class ProblemNeighborResponse(BaseModel):
    previous_problem_id: str | None = None
    next_problem_id: str | None = None
    position: int
    total: int


class ProblemCategoriesResponse(BaseModel):
    categories: list[str] = Field(default_factory=list)


class ProblemDetailResponse(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)

    statement: str
    input_format: str
    output_format: str
    constraints: str

    examples: list[TestCaseSchema]
    visible_test_cases: list[TestCaseSchema]

    starter_code: dict[str, str]

    time_limit_ms: int
    memory_limit_mb: int

    is_solved: bool


# ==========================================================
# Run Code
# ==========================================================

class RunRequest(BaseModel):
    language: Literal["python", "java", "cpp", "javascript"]
    code: str = Field(..., min_length=1, max_length=20000)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return _validate_language(value)


class TestCaseResult(BaseModel):
    input: str
    expected_output: str
    actual_output: str | None = None

    passed: bool

    runtime_ms: float | None = None
    memory_kb: float | None = None

    stderr: str | None = None


class RunResponse(BaseModel):
    results: list[TestCaseResult]
    all_passed: bool
    compile_error: str | None = None


# ==========================================================
# Submit
# ==========================================================

class SubmitRequest(BaseModel):
    language: Literal["python", "java", "cpp", "javascript"]
    code: str = Field(..., min_length=1, max_length=20000)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return _validate_language(value)


class AIFeedbackResponse(BaseModel):
    correctness: str | None = None
    algorithm_used: str | None = None
    explanation: str | None = None
    time_complexity: str | None = None
    space_complexity: str | None = None
    code_quality: str | None = None
    suggestions: list[str] = Field(default_factory=list)
    optimization_suggestions: list[str] = Field(default_factory=list)
    edge_cases_missed: list[str] = Field(default_factory=list)
    relevant_edge_cases: list[str] = Field(default_factory=list)
    interview_tips: list[str] = Field(default_factory=list)
    overall_rating: str | None = None


class SubmitResponse(BaseModel):
    submission_id: str

    status: str
    verdict: str

    runtime_ms: float | None = None
    memory_kb: float | None = None

    passed_test_cases: int = 0
    total_test_cases: int = 0

    failed_case_index: int | None = None
    failed_test_number: int | None = None

    compile_error: str = ""
    stderr: str = ""
    failure_reason: str = ""

    ai_feedback: AIFeedbackResponse = Field(default_factory=AIFeedbackResponse)


# ==========================================================
# Submission History
# ==========================================================

class SubmissionHistoryItem(BaseModel):
    id: str
    problem_id: str

    language: str

    status: str

    runtime_ms: float | None = None
    memory_kb: float | None = None

    submitted_at: datetime


class SubmissionHistoryResponse(BaseModel):
    submissions: list[SubmissionHistoryItem]


# ==========================================================
# Coding Progress
# ==========================================================

class ProgressResponse(BaseModel):
    total_solved: int

    easy_solved: int
    medium_solved: int
    hard_solved: int

    current_streak: int
    longest_streak: int

    total_submissions: int
    total_accepted: int

    acceptance_rate: float