import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.coding_progress import CODING_PROGRESS_COLLECTION
from app.schemas.coding import ProgressResponse

logger = logging.getLogger(__name__)


async def record_solved(
    db: AsyncIOMotorDatabase, user_id: str, problem_id: str, difficulty: str
) -> None:
    collection = db[CODING_PROGRESS_COLLECTION]
    document = await collection.find_one({"user_id": user_id})

    if document and problem_id in document.get("solved_problem_ids", []):
        # Already solved before — re-submission shouldn't double-count progress.
        return

    difficulty_counter = {
        "easy": "easy_solved",
        "medium": "medium_solved",
        "hard": "hard_solved",
    }.get(difficulty)

    inc_fields = {"total_solved": 1}
    if difficulty_counter:
        inc_fields[difficulty_counter] = 1

    await collection.update_one(
        {"user_id": user_id},
        {
            "$addToSet": {"solved_problem_ids": problem_id},
            "$inc": inc_fields,
            "$set": {"updated_at": datetime.now(timezone.utc)},
            "$setOnInsert": {"user_id": user_id},
        },
        upsert=True,
    )
    logger.info("Recorded solve for user %s: problem %s (%s)", user_id, problem_id, difficulty)


async def get_progress(db: AsyncIOMotorDatabase, user_id: str) -> ProgressResponse:
    collection = db[CODING_PROGRESS_COLLECTION]
    document = await collection.find_one({"user_id": user_id})

    if not document:
        return ProgressResponse(
            total_solved=0,
            easy_solved=0,
            medium_solved=0,
            hard_solved=0,
            current_streak=0,
            longest_streak=0,
            total_submissions=0,
            total_accepted=0,
            acceptance_rate=0.0,
        )

    return ProgressResponse(
        total_solved=document.get("total_solved", 0),
        easy_solved=document.get("easy_solved", 0),
        medium_solved=document.get("medium_solved", 0),
        hard_solved=document.get("hard_solved", 0),
        current_streak=document.get("current_streak", 0),
        longest_streak=document.get("longest_streak", 0),
        total_submissions=document.get("total_submissions", 0),
        total_accepted=document.get("total_accepted", 0),
        acceptance_rate=document.get("acceptance_rate", 0.0),
    )