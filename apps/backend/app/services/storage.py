import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

UPLOAD_DIR = Path(settings.upload_dir or "/app/uploads")
ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_file(file: UploadFile, subdir: str = "general") -> dict:
    ensure_upload_dir()
    target_dir = UPLOAD_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename or "file")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = target_dir / unique_name

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise ValueError("File too large (max 10MB)")
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise ValueError(f"File type {file.content_type} not allowed")

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "stored_name": unique_name,
        "path": str(file_path),
        "size": len(content),
        "content_type": file.content_type,
        "url": f"/api/files/{subdir}/{unique_name}",
    }


def get_file_path(subdir: str, filename: str) -> Path:
    return UPLOAD_DIR / subdir / filename
