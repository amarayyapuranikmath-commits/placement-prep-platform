from typing import Optional

from pydantic import BaseModel, Field

from app.services.interview_engine import InterviewerPersona


class InterviewSessionCreateRequest(BaseModel):
    interview_type: str
    role: Optional[str] = None
    experience_level: Optional[str] = None
    company_type: Optional[str] = None
    difficulty: Optional[str] = None
    duration: Optional[str] = None
    language: Optional[str] = None
    question_id: Optional[str] = None
    persona: Optional[InterviewerPersona] = None


class InterviewTurnRequest(BaseModel):
    raw_answer: str
    persona: Optional[InterviewerPersona] = None


class InterviewQuestionEvaluation(BaseModel):
    question_id: str
    question_text: str
    candidate_answer: str
    evaluation: str
    score: float
    feedback: Optional[str] = None
    recommendations: list[str] = Field(default_factory=list)


class InterviewReportResponse(BaseModel):
    session_id: str
    candidate_id: str
    interview_type: Optional[str] = None
    role: Optional[str] = None
    completion_status: str
    interview_duration_seconds: int
    overall_score: int
    technical_score: int
    communication_score: int
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    question_evaluations: list[InterviewQuestionEvaluation] = Field(default_factory=list)
    completed_at: Optional[str] = None


class InterviewHistoryItem(BaseModel):
    session_id: str
    interview_type: Optional[str] = None
    role: Optional[str] = None
    date: str
    score: int
    status: str
    duration: str


class InterviewHistoryResponse(BaseModel):
    history: list[InterviewHistoryItem] = Field(default_factory=list)
