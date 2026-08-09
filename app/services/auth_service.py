import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import USERS_COLLECTION
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenPair,
    UserResponse,
)

logger = logging.getLogger(__name__)


def _to_user_response(document: dict[str, Any]) -> UserResponse:
    return UserResponse(
        id=str(document["_id"]),
        full_name=document["full_name"],
        email=document["email"],
        phone=document.get("phone"),
        college=document.get("college"),
        branch=document.get("branch"),
        graduation_year=document.get("graduation_year"),
        target_role=document.get("target_role"),
        target_company=document.get("target_company"),
        skills=document.get("skills", []),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
        is_active=document.get("is_active", True),
    )


def _issue_tokens(user_id: str) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(subject=user_id),
        refresh_token=create_refresh_token(subject=user_id),
    )


async def register_user(db: AsyncIOMotorDatabase, payload: RegisterRequest) -> AuthResponse:
    collection = db[USERS_COLLECTION]
    normalized_email = payload.email.lower()

    existing = await collection.find_one({"email": normalized_email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    now = datetime.now(timezone.utc)
    user_doc = {
        "full_name": payload.full_name,
        "email": normalized_email,
        "password_hash": hash_password(payload.password),
        "phone": payload.phone,
        "college": payload.college,
        "branch": payload.branch,
        "graduation_year": payload.graduation_year,
        "target_role": payload.target_role,
        "target_company": payload.target_company,
        "skills": payload.skills,
        "theme": "default",
        "created_at": now,
        "updated_at": now,
        "is_active": True,
    }

    result = await collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    logger.info("New user registered: %s", normalized_email)

    tokens = _issue_tokens(str(user_doc["_id"]))
    return AuthResponse(user=_to_user_response(user_doc), tokens=tokens)


async def authenticate_user(db: AsyncIOMotorDatabase, payload: LoginRequest) -> AuthResponse:
    collection = db[USERS_COLLECTION]
    normalized_email = payload.email.lower()

    user_doc = await collection.find_one({"email": normalized_email})
    if not user_doc or not verify_password(payload.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    logger.info("User authenticated: %s", normalized_email)

    tokens = _issue_tokens(str(user_doc["_id"]))
    return AuthResponse(user=_to_user_response(user_doc), tokens=tokens)


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> UserResponse:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity",
        )

    collection = db[USERS_COLLECTION]
    user_doc = await collection.find_one({"_id": ObjectId(user_id)})

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return _to_user_response(user_doc)


async def refresh_access_token(db: AsyncIOMotorDatabase, refresh_token: str) -> TokenPair:
    try:
        payload = decode_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload["sub"]
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity",
        )

    collection = db[USERS_COLLECTION]
    user_doc = await collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc or not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists or is inactive",
        )

    logger.info("Token refreshed for user: %s", user_doc["email"])

    return _issue_tokens(user_id)