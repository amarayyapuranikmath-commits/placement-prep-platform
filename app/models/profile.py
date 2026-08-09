from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import PyObjectId

PROFILES_COLLECTION = "profiles"


class ProfileModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    COLLECTION_NAME: ClassVar[str] = PROFILES_COLLECTION

    id: PyObjectId | None = Field(default=None, alias="_id")
    user_id: str
    profile_picture_url: str | None = None
    phone: str | None = None
    college: str | None = None
    degree: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    cgpa: float | None = None
    target_role: str | None = None
    target_companies: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    github_url: str | None = None
    linkedin_url: str | None = None
    resume_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))