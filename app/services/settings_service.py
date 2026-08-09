from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.models.user import USERS_COLLECTION
from app.schemas.auth import PASSWORD_PATTERN
from app.schemas.settings import PasswordUpdateRequest, ProfileUpdateRequest, ThemeUpdateRequest


async def get_settings_data(db: Any, user_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identity")

    collection = db[USERS_COLLECTION]
    user_doc = await collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    theme_value = user_doc.get("theme", "default")
    if theme_value not in {"default", "light"}:
        theme_value = "default"

    return {
        "full_name": user_doc.get("full_name", ""),
        "email": user_doc.get("email", ""),
        "theme": theme_value,
    }


async def update_profile(db: Any, user_id: str, payload: ProfileUpdateRequest) -> dict[str, Any]:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identity")

    collection = db[USERS_COLLECTION]
    user_doc = await collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    now = datetime.now(timezone.utc)
    await collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"full_name": payload.full_name, "updated_at": now}},
    )

    return {"full_name": payload.full_name, "email": user_doc.get("email", "")}


async def update_password(db: Any, user_id: str, payload: PasswordUpdateRequest) -> dict[str, Any]:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identity")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")

    if not PASSWORD_PATTERN.match(payload.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
        )

    collection = db[USERS_COLLECTION]
    user_doc = await collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(payload.current_password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    now = datetime.now(timezone.utc)
    new_password_hash = hash_password(payload.new_password)
    await collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": new_password_hash, "updated_at": now}},
    )

    return {"message": "Password updated successfully"}


async def update_theme(db: Any, user_id: str, payload: ThemeUpdateRequest) -> dict[str, Any]:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identity")

    collection = db[USERS_COLLECTION]
    user_doc = await collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    normalized_theme = payload.theme if payload.theme in {"default", "light"} else "default"
    await collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"theme": normalized_theme}})
    return {"theme": normalized_theme}
