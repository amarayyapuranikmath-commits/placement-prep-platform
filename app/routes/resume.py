import logging

from fastapi import APIRouter, Depends, File, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.services import resume_service
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    analysis = await resume_service.upload_and_analyze_resume(db, user_id, file)
    return success_response(
        data=analysis.model_dump(),
        message="Resume uploaded and analyzed",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/history")
async def get_resume_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    history = await resume_service.get_resume_history(db, user_id)
    return success_response(data=history.model_dump(), message="Resume history retrieved")


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    analysis = await resume_service.get_resume_analysis(db, user_id, resume_id)
    return success_response(data=analysis.model_dump(), message="Resume analysis retrieved")


@router.post("/{resume_id}/reanalyze")
async def reanalyze_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    analysis = await resume_service.reanalyze_resume(db, user_id, resume_id)
    return success_response(data=analysis.model_dump(), message="Resume re-analyzed")


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await resume_service.delete_resume(db, user_id, resume_id)
    return success_response(data=None, message="Resume deleted")