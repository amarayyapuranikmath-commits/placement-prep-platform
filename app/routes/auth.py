import logging
from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, UserResponse
from app.services import auth_service
from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        logger.info("Register endpoint called for email=%s", payload.email)
        result = await auth_service.register_user(db, payload)
        logger.info("Register successful for email=%s", payload.email)
        return success_response(
            data=result.model_dump(),
            message="Registration successful",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception:
        logger.exception("Error during user registration")
        # Let the global exception handler return a sanitized error response
        raise


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    payload = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )

    result = await auth_service.authenticate_user(db, payload)

    return success_response(
        data={
            "user": result.user.model_dump(),
            "tokens": result.tokens.model_dump(),
        },
        message="Login successful",
    )

@router.get("/me")
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return success_response(data=current_user.model_dump(), message="Current user retrieved")


@router.post("/refresh")
async def refresh(
    payload: RefreshRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    tokens = await auth_service.refresh_access_token(db, payload.refresh_token)
    return success_response(data=tokens.model_dump(), message="Token refreshed")