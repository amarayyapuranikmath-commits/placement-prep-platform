from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import PyObjectId

RESUMES_COLLECTION = "resumes"


class ResumeModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    COLLECTION_NAME: ClassVar[str] = RESUMES_COLLECTION

    id: PyObjectId | None = Field(default=None, alias="_id")
    user_id: str
    file_name: str
    file_size_bytes: int
    storage_path: str
    version: int
    is_current: bool = True
    extracted_text: str | None = None
    ats_score: int | None = None
    quality_label: str | None = None
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    analysis_status: str = "pending"
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))