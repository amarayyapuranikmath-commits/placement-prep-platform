import uuid
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def get_resume_storage_dir() -> Path:
    storage_dir = Path(settings.RESUME_STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def save_resume_file(user_id: str, original_filename: str, file_bytes: bytes) -> str:
    storage_dir = get_resume_storage_dir()
    safe_suffix = Path(original_filename).suffix or ".pdf"
    unique_name = f"{user_id}_{uuid.uuid4().hex}{safe_suffix}"
    file_path = storage_dir / unique_name
    file_path.write_bytes(file_bytes)
    return str(file_path)


def delete_resume_file(storage_path: str) -> None:
    path = Path(storage_path)
    if path.exists():
        path.unlink()