import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.profile import PROFILES_COLLECTION
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

logger = logging.getLogger(__name__)

_COMPLETION_FIELDS = [
    "profile_picture_url",
    "phone",
    "college",
    "degree",
    "branch",
    "graduation_year",
    "cgpa",
    "target_role",
    "target_companies",
    "skills",
    "github_url",
    "linkedin_url",
    "resume_id",
]


def _calculate_completion(document: dict[str, Any]) -> int:
    filled = 0
    for field in _COMPLETION_FIELDS:
        value = document.get(field)
        if isinstance(value, list):
            if len(value) > 0:
                filled += 1
        elif value not in (None, ""):
            filled += 1
    return round((filled / len(_COMPLETION_FIELDS)) * 100)


def _to_profile_response(document: dict[str, Any]) -> ProfileResponse:
    return ProfileResponse(
        user_id=document["user_id"],
        profile_picture_url=document.get("profile_picture_url"),
        phone=document.get("phone"),
        college=document.get("college"),
        degree=document.get("degree"),
        branch=document.get("branch"),
        graduation_year=document.get("graduation_year"),
        cgpa=document.get("cgpa"),
        target_role=document.get("target_role"),
        target_companies=document.get("target_companies", []),
        skills=document.get("skills", []),
        github_url=document.get("github_url"),
        linkedin_url=document.get("linkedin_url"),
        resume_id=document.get("resume_id"),
        completion_percentage=_calculate_completion(document),
    )


async def get_profile(db: AsyncIOMotorDatabase, user_id: str) -> ProfileResponse:
    collection = db[PROFILES_COLLECTION]
    document = await collection.find_one({"user_id": user_id})

    if not document:
        now = datetime.now(timezone.utc)
        document = {
            "user_id": user_id,
            "profile_picture_url": None,
            "phone": None,
            "college": None,
            "degree": None,
            "branch": None,
            "graduation_year": None,
            "cgpa": None,
            "target_role": None,
            "target_companies": [],
            "skills": [],
            "github_url": None,
            "linkedin_url": None,
            "resume_id": None,
            "created_at": now,
            "updated_at": now,
        }
        await collection.insert_one(document)

    return _to_profile_response(document)


async def update_profile(
    db: AsyncIOMotorDatabase, user_id: str, payload: ProfileUpdateRequest
) -> ProfileResponse:
    collection = db[PROFILES_COLLECTION]

    update_fields = payload.model_dump(exclude_unset=True)
    update_fields["updated_at"] = datetime.now(timezone.utc)

    document = await collection.find_one_and_update(
        {"user_id": user_id},
        {
            "$set": update_fields,
            "$setOnInsert": {"user_id": user_id, "created_at": datetime.now(timezone.utc)},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    logger.info("Profile updated for user: %s", user_id)

    return _to_profile_response(document)


async def set_resume_id(db: AsyncIOMotorDatabase, user_id: str, resume_id: str | None) -> None:
    """Internal helper used by the Resume module to link the latest resume to a profile."""
    collection = db[PROFILES_COLLECTION]
    await collection.update_one(
        {"user_id": user_id},
        {
            "$set": {"resume_id": resume_id, "updated_at": datetime.now(timezone.utc)},
            "$setOnInsert": {"user_id": user_id, "created_at": datetime.now(timezone.utc)},
        },
        upsert=True,
    )