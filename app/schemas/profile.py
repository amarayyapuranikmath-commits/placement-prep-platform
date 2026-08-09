from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProfileUpdateRequest(BaseModel):
    profile_picture_url: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=20)
    college: str | None = Field(default=None, max_length=150)
    degree: str | None = Field(default=None, max_length=100)
    branch: str | None = Field(default=None, max_length=100)
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    cgpa: float | None = Field(default=None, ge=0, le=10)
    target_role: str | None = Field(default=None, max_length=100)
    target_companies: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    github_url: str | None = Field(default=None, max_length=300)
    linkedin_url: str | None = Field(default=None, max_length=300)

    @field_validator("target_companies", "skills")
    @classmethod
    def strip_and_dedupe(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        seen: set[str] = set()
        deduped = []
        for item in cleaned:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped

    @field_validator("github_url", "linkedin_url")
    @classmethod
    def validate_optional_url(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        # Delegates format validation to Pydantic's HttpUrl, but stores as str
        # so the field stays simple to serialize and compare against "".
        HttpUrl(value)
        return value


class ProfileResponse(BaseModel):
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
    completion_percentage: int