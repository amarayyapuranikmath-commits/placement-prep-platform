import logging
from typing import Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.utils.response import success_response
from app.services.dashboard_service import build_dashboard

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
@router.get("/")
async def get_dashboard(
	user_id: str = Depends(get_current_user_id),
	db: AsyncIOMotorDatabase = Depends(get_db),
):
	payload = await build_dashboard(db, user_id)
	return success_response(data=payload, message="Dashboard retrieved")

