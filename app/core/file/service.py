import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, status, UploadFile

from core.config import settings

BANNERS_FOLDER = "images/banners"
EVENTS_FOLDER = "images/events"
NEWS_FOLDER = "images/news"
PARTNERS_FOLDER = "images/partners"


class FileService:
    def __init__(self):
        self.uploads_dir: Path = settings.file.uploads_dir
        self.allowed_image_types: set = settings.file.allowed_image_types
        self.max_file_size: int = settings.file.max_file_size

    async def save_upload_file(
        self,
        upload_file: UploadFile,
        subdirectory: str,
    ) -> str:
        await self._validate_file(upload_file)

        file_extension = os.path.splitext(upload_file.filename)[1]
        filename = f"{uuid.uuid4().hex}{file_extension}"

        save_path = self.uploads_dir / subdirectory / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(save_path, "wb") as f:
            content = await upload_file.read()
            await f.write(content)

        relative_path = str(Path(subdirectory) / filename)
        return relative_path.replace("\\", "/")

    async def _validate_file(
        self,
        upload_file: UploadFile,
    ):
        content = await upload_file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large",
            )

        if upload_file.content_type not in self.allowed_image_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type",
            )

        await upload_file.seek(0)

    async def delete_file(
        self,
        file_path: str,
    ):
        absolute_path = self.uploads_dir / file_path
        try:
            if absolute_path.exists():
                absolute_path.unlink()
        except OSError:
            pass


file_service = FileService()
