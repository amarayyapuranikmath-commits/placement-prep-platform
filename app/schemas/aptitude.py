from pydantic import BaseModel, Field


class AptitudeSessionCreateRequest(BaseModel):
    test_type: str = Field(..., min_length=1)
    difficulty: str = Field(..., min_length=1)
    question_count: int = Field(default=10, ge=1, le=50)


class AptitudeAnswerRequest(BaseModel):
    question_id: str
    answer: str | None = None
    review: bool | None = None


class AptitudeSubmitRequest(BaseModel):
    submitted_at: str | None = None
