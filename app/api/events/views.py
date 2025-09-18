from typing import Annotated
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, status, Depends, Form, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from core.file.service import file_service, EVENTS_FOLDER
from api.dependencies import get_current_active_user
from api.events.schemas import EventResponse
from api.events import crud


router = APIRouter()


@router.get("/", response_model=list[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    events = await crud.get_events(session=session, skip=skip, limit=limit)
    return events


@router.get("/{event_id}/", response_model=EventResponse)
async def get_event_by_id(
    event_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    event = await crud.get_event_by_id(session=session, event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@router.post("/", response_model=EventResponse)
async def create_event(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    image: UploadFile,
    is_active: Annotated[bool, Form()],
    event_date: Annotated[datetime | None, Form()] = None,
    location: Annotated[str | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    image_url = await file_service.save_image_file(image, EVENTS_FOLDER)
    event = await crud.create_event(
        session=session,
        title=title,
        description=description,
        image_url=image_url,
        is_active=is_active,
        event_date=event_date,
        location=location,
    )

    return event


@router.patch("/{event_id}/", response_model=EventResponse)
async def update_event(
    event_id: uuid.UUID,
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    image: UploadFile | None = None,
    is_active: Annotated[bool | None, Form()] = None,
    event_date: Annotated[datetime | None, Form()] = None,
    location: Annotated[str | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_event = await crud.get_event_by_id(session=session, event_id=event_id)
    if not current_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if image:
        await file_service.delete_file(current_event.image_url)
        image_url = await file_service.save_image_file(image, EVENTS_FOLDER)

    event = crud.update_event(
        session=session,
        current_event=current_event,
        title=title,
        description=description,
        image_url=image_url,
        is_active=is_active,
        event_date=event_date,
        location=location,
    )

    return event


@router.delete("/{event_id}/")
async def delete_event(
    event_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_event(session=session, event_id=event_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return {"message": "success"}
