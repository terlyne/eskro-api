from pathlib import Path
import aiofiles
import json

from fastapi import APIRouter, Depends

from core.models import User
from core.config import BASE_DIR
from core.contacts.service import contacts_service
from api.dependencies import get_current_active_user
from api.contacts.schemas import ContactsCreate, ContactsUpdate, ContactsResponse


router = APIRouter()


@router.get("/", response_model=ContactsResponse)
async def get_contacts():
    contacts_data = await contacts_service.read_contacts()
    return ContactsCreate(**contacts_data)


@router.patch("/", response_model=ContactsResponse)
async def update_contacts(
    contacts_in: ContactsUpdate,
    user: User = Depends(get_current_active_user),
):
    update_data = contacts_in.model_dump(exclude_none=True)

    current_contacts = await contacts_service.read_contacts()

    for field, value in update_data.items():
        if field in current_contacts:
            current_contacts[field] = value

    await contacts_service.write_contacts(current_contacts)
    return ContactsResponse(**current_contacts)
