
import logging

from fastapi import APIRouter, Depends, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.services.progress_service import ProgressService
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_progress_summary(user_id: str = Depends(get_current_user_id), db: AsyncIOMotorDatabase = Depends(get_db)):
	service = ProgressService(db)
	summary = await service.get_summary(user_id)
	return success_response(data=summary, message="Progress summary retrieved")


@router.get("/analytics")
async def get_progress_analytics(module: str | None = None, user_id: str = Depends(get_current_user_id), db: AsyncIOMotorDatabase = Depends(get_db)):
	service = ProgressService(db)
	points = await service.get_analytics(user_id, module or "interview")
	return success_response(data={"points": points}, message="Progress analytics retrieved")


@router.get("/report")
async def download_progress_report(user_id: str = Depends(get_current_user_id), db: AsyncIOMotorDatabase = Depends(get_db)):
	service = ProgressService(db)
	pdf_bytes = await service.generate_report(user_id)
	return Response(content=pdf_bytes, media_type="application/pdf")


