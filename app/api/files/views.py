from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path

from core.config import settings

router = APIRouter()


@router.get("/files/{file_path:path}")
async def get_file(file_path: str):
    full_file_path = settings.file.uploads_dir / file_path

    try:
        full_file_path.resolve().relative_to(settings.file.uploads_dir.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path",
        )

    if not full_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if not full_file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a file",
        )

    # Определяем MIME тип
    extension = full_file_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
    }

    media_type = media_types.get(extension, "application/octet-stream")

    return FileResponse(
        full_file_path,
        media_type=media_type,
        filename=full_file_path.name,
    )
