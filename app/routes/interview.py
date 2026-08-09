import logging

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.schemas.interview import InterviewSessionCreateRequest, InterviewTurnRequest
from app.services.interview_service import InterviewService
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_interview_session(
    payload: InterviewSessionCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = InterviewService(db)
    initialized_session = await service.create_session(
        user_id,
        payload.model_dump(exclude_none=True, exclude={"persona"}),
        payload.persona,
    )
    return success_response(
        data=initialized_session,
        message="Interview session created",
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/sessions/{session_id}/turns")
async def submit_interview_turn(
    session_id: str,
    payload: InterviewTurnRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = InterviewService(db)
    result = await service.process_turn(
        session_id=session_id,
        candidate_id=user_id,
        raw_answer=payload.raw_answer,
        persona=payload.persona,
    )
    return success_response(data=result, message="Interview turn processed")


@router.post("/sessions/{session_id}/complete")
async def complete_interview_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = InterviewService(db)
    report = await service.complete_session(session_id=session_id, candidate_id=user_id)
    return success_response(data=report, message="Interview report generated")


@router.get("/sessions/{session_id}/report")
async def get_interview_report(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = InterviewService(db)
    report = await service.get_report(session_id=session_id, candidate_id=user_id)
    return success_response(data=report, message="Interview report retrieved")


@router.get("/history")
async def get_interview_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = InterviewService(db)
    history = await service.get_history(candidate_id=user_id)
    return success_response(data={"history": history}, message="Interview history retrieved")


@router.get("/questions/{question_id}")
async def get_interview_question(
    question_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = InterviewService(db)
    question = await service.fetch_question(question_id)
    return success_response(data=question.model_dump(mode="json"), message="Interview question retrieved")
