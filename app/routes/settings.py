from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.schemas.auth import UserResponse
from app.schemas.settings import PasswordUpdateRequest, ProfileUpdateRequest, ThemeUpdateRequest
from app.services import settings_service
from app.utils.response import success_response

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def get_settings(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = await settings_service.get_settings_data(db, user_id)
    return success_response(data=data, message="Settings retrieved")


@router.put("/profile", status_code=status.HTTP_200_OK)
async def update_profile(
    payload: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = await settings_service.update_profile(db, user_id, payload)
    return success_response(data=data, message="Profile updated")


@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(
    payload: PasswordUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = await settings_service.update_password(db, user_id, payload)
    return success_response(data=data, message="Password updated")


@router.put("/theme", status_code=status.HTTP_200_OK)
async def update_theme(
    payload: ThemeUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = await settings_service.update_theme(db, user_id, payload)
    return success_response(data=data, message="Theme updated")
