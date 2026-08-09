import logging

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.schemas.profile import ProfileUpdateRequest
from app.services import profile_service
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    profile = await profile_service.get_profile(db, user_id)
    return success_response(data=profile.model_dump(), message="Profile retrieved")


@router.put("")
async def update_my_profile(
    payload: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    profile = await profile_service.update_profile(db, user_id, payload)
    return success_response(data=profile.model_dump(), message="Profile updated")