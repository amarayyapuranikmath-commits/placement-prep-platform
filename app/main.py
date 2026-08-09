import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_mongo_connection, connect_to_mongo, get_database
from app.routes import aptitude, auth, coding, profile, resume, interview, insights, dashboard, settings as settings_routes
from app.services.aptitude_question_seed import seed_aptitude_questions
from app.services.interview_question_seed import seed_interview_questions
from app.utils.logger import configure_logging
from app.utils.response import error_response, success_response

configure_logging()
logger = logging.getLogger(__name__)
app_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    try:
        db = get_database()
        await seed_interview_questions(db)
        await seed_aptitude_questions(db)
    except Exception as exc:
        logger.exception("Question seed failed during startup: %s", exc)
    logger.info("%s startup complete.", app_settings.APP_NAME)
    yield
    await close_mongo_connection()
    logger.info("%s shutdown complete.", app_settings.APP_NAME)


app = FastAPI(
    title=app_settings.APP_NAME,
    version=app_settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(message=str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=exc.errors(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.get("/health", tags=["System"])
async def health_check():
    return success_response(data={"status": "ok"}, message="Service is healthy")


@app.get("/version", tags=["System"])
async def get_version():
    return success_response(
        data={
            "app_name": app_settings.APP_NAME,
            "version": app_settings.APP_VERSION,
            "environment": app_settings.APP_ENV,
        }
    )


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(coding.router, prefix="/api/v1/coding", tags=["Coding"])
app.include_router(interview.router, prefix="/api/v1/interview", tags=["Interview"])
app.include_router(aptitude.router, prefix="/api/v1/aptitude", tags=["Aptitude"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["Insights"])
app.include_router(__import__('app.routes.progress', fromlist=['router']).router, prefix="/api/v1/progress", tags=["Progress"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(settings_routes.router, prefix="/api/v1/settings", tags=["Settings"])

