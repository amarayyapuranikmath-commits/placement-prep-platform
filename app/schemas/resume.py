from datetime import datetime

from pydantic import BaseModel, Field


class ScoreBreakdownResponse(BaseModel):
    keywords: int = 0
    formatting: int = 0
    skills: int = 0
    projects: int = 0
    experience: int = 0
    education: int = 0


class SectionScoresResponse(BaseModel):
    personal_information: int = 0
    education: int = 0
    experience: int = 0
    projects: int = 0
    skills: int = 0
    certifications: int = 0
    achievements: int = 0
    formatting: int = 0
    ats_compatibility: int = 0
    structure: int = 0
    grammar: int = 0
    readability: int = 0
    technical_depth: int = 0


class KeywordAnalysisResponse(BaseModel):
    strong: list[str] = Field(default_factory=list)
    weak: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class ResumeAnalysisResponse(BaseModel):
    id: str
    file_name: str
    file_size_bytes: int
    version: int
    is_current: bool
    ats_score: int | None = None
    quality_label: str | None = None
    score_breakdown: ScoreBreakdownResponse
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    role_match: int | None = None
    keyword_match: int | None = None
    section_scores: SectionScoresResponse = Field(default_factory=SectionScoresResponse)
    keywords: KeywordAnalysisResponse = Field(default_factory=KeywordAnalysisResponse)
    is_resume: bool | None = None
    reason: str | None = None
    analysis_status: str
    uploaded_at: datetime


class ResumeSummaryResponse(BaseModel):
    id: str
    file_name: str
    version: int
    is_current: bool
    ats_score: int | None = None
    quality_label: str | None = None
    analysis_status: str
    uploaded_at: datetime


class ResumeHistoryResponse(BaseModel):
    resumes: list[ResumeSummaryResponse]