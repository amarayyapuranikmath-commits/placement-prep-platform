import logging
from typing import Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.utils.response import success_response
from app.services.insights_service import generate_insights, answer_insight_question

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
@router.get("/")
async def get_insights(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    insights = await generate_insights(db, user_id)
    return success_response(data=insights, message="AI insights retrieved")


@router.post("/query")
@router.post("/query/")
async def ask_insight_question(
    payload: dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    question = payload.get("question")
    if not question:
        return success_response(data={"answer": ""}, message="No question provided")

    answer = await answer_insight_question(db, user_id, question)
    return success_response(data={"answer": answer}, message="Insight question answered")
