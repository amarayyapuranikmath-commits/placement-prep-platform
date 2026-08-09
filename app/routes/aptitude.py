import logging

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.schemas.aptitude import AptitudeAnswerRequest, AptitudeSessionCreateRequest
from app.services.aptitude_service import AptitudeService
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_aptitude_session(
    payload: AptitudeSessionCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        session = await service.create_session(user_id, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(data=session, message="Aptitude session created", status_code=status.HTTP_201_CREATED)


@router.post("/sessions/{session_id}/answers")
async def save_aptitude_answer(
    session_id: str,
    payload: AptitudeAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        result = await service.update_answer(session_id, user_id, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(data=result, message="Answer saved")


@router.delete("/sessions/{session_id}/answers/{question_id}")
async def clear_aptitude_answer(
    session_id: str,
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        result = await service.clear_answer(session_id, user_id, question_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(data=result, message="Answer cleared")


@router.get("/sessions/{session_id}")
async def get_aptitude_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        session = await service.get_session(session_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(data=session, message="Aptitude session retrieved")


@router.post("/sessions/{session_id}/submit")
async def submit_aptitude_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        result = await service.submit_session(session_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(data=result, message="Aptitude session submitted")


@router.get("/sessions/{session_id}/review")
async def get_aptitude_review(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        result = await service.get_review(session_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(data=result, message="Review generated")


@router.get("/sessions/{session_id}/result")
async def get_aptitude_result(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    try:
        result = await service.get_result(session_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(data=result, message="Aptitude result retrieved")


@router.get("/history")
async def get_aptitude_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AptitudeService(db)
    history = await service.get_history(user_id)
    return success_response(data={"history": history}, message="Aptitude history retrieved")
