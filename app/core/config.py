import re
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        frozen=True,
    )

    # Application
    APP_NAME: str = "Placement Prep Platform API"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str
    MONGODB_CONNECT_ON_STARTUP: bool = True

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Logging
    LOG_LEVEL: str = "INFO"

    # AI / Judge0
    GROQ_API_KEY: str | None = None
    JUDGE0_API_URL: str | None = None
    JUDGE0_API_KEY: str | None = None
    REQUEST_TIMEOUT: int = 30

    @field_validator("REQUEST_TIMEOUT", mode="before")
    @classmethod
    def _coerce_request_timeout(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return 30
            digits = re.match(r"^-?\d+", value)
            if digits:
                return int(digits.group(0))
        return value

    # Storage
    RESUME_STORAGE_DIR: Path = Path("storage/resumes")
    MAX_RESUME_SIZE_MB: int = 5

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return []

        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()