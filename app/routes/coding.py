import logging

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.schemas.coding import PreferenceUpdateRequest, RunRequest, SubmitRequest
from app.services import coding_service, coding_progress_service, judge0_service
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/preferences")
async def get_preferences(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.get_preferences(db, user_id)
    return success_response(data=result.model_dump(), message="Preferences retrieved")


@router.put("/preferences")
async def update_preferences(
    payload: PreferenceUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.update_preferences(db, user_id, payload)
    return success_response(data=result.model_dump(), message="Preferences updated")


@router.get("/categories")
async def list_categories(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.get_problem_categories(db)
    return success_response(data=result.model_dump(), message="Categories retrieved")


@router.get("/problems")
async def list_problems(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    language: str | None = None,
    sort: str = "problem_number",
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.list_problems(
        db=db,
        user_id=user_id,
        search=search,
        category=category,
        difficulty=difficulty,
        language=language,
        page=page,
        page_size=limit,
        sort=sort,
    )
    return success_response(data=result.model_dump(), message="Problems retrieved")


@router.get("/problems/{problem_id}")
async def get_problem_detail(
    problem_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.get_problem_detail(db, user_id, problem_id)
    return success_response(data=result.model_dump(), message="Problem details retrieved")


@router.get("/problems/{problem_id}/neighbors")
async def get_problem_neighbors(
    problem_id: str,
    search: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    language: str | None = None,
    sort: str = "problem_number",
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.get_problem_neighbors(
        db=db,
        user_id=user_id,
        problem_id=problem_id,
        search=search,
        category=category,
        difficulty=difficulty,
        language=language,
        sort=sort,
    )
    return success_response(data=result.model_dump(), message="Problem neighbors retrieved")


@router.post("/problems/{problem_id}/run", status_code=status.HTTP_200_OK)
async def run_code(
    problem_id: str,
    payload: RunRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await judge0_service.run_code(db, problem_id, payload)
    return success_response(data=result.model_dump(), message="Code executed")


@router.post("/problems/{problem_id}/submit", status_code=status.HTTP_200_OK)
async def submit_code(
    problem_id: str,
    payload: SubmitRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await judge0_service.submit_code(db, user_id, problem_id, payload)
    return success_response(data=result.model_dump(), message="Submission recorded")


@router.get("/submissions")
async def get_submission_history(
    problem_id: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_service.get_submission_history(db, user_id, problem_id)
    return success_response(data=result.model_dump(), message="Submission history retrieved")


@router.get("/progress")
async def get_progress(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await coding_progress_service.get_progress(db, user_id)
    return success_response(data=result.model_dump(), message="Coding progress retrieved")
