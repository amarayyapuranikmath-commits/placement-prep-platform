from datetime import datetime, timezone
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

CODING_PREFERENCES_COLLECTION = "coding_preferences"

SUPPORTED_LANGUAGES = ["python", "java", "cpp", "javascript"]


class CodingPreferenceModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    COLLECTION_NAME: ClassVar[str] = CODING_PREFERENCES_COLLECTION

    # User
    user_id: str

    # Preferred programming language
    preferred_language: Literal[
        "python",
        "java",
        "cpp",
        "javascript",
    ] = "python"

    # Last updated timestamp
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )