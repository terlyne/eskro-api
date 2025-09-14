from typing import Any
from pathlib import Path
import aiofiles
import json

from fastapi import HTTPException, status

from core.config import BASE_DIR


CONTACTS_PATH = BASE_DIR / "app" / "core" / "contacts" / "contacts.json"


class ContactsService:
    def __init__(self, contacts_path: Path):
        self.contacts_path = contacts_path

    async def read_contacts(self) -> dict[str, Any]:
        try:
            async with aiofiles.open(self.contacts_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content)

        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacts not found",
            )

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid contacts file format",
            )

    async def write_contacts(self, contacts: dict[str, Any]) -> dict[str, Any]:
        try:
            async with aiofiles.open(self.contacts_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(contacts, ensure_ascii=False, indent=4))

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save contacts",
            )


contacts_service = ContactsService(contacts_path=CONTACTS_PATH)
