import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from api.dependencies import get_current_active_user
from api.polls.schemas import PollResponse, PollCreate, PollUpdate
from api.polls import crud

router = APIRouter()


@router.get("/", response_model=list[PollResponse])
async def get_polls(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    polls = await crud.get_polls(session=session)
    return polls


@router.get("/{poll_id}/", response_model=PollResponse)
async def get_poll_by_id(
    poll_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    poll = await crud.get_poll_by_id(session=session, poll_id=poll_id)
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    return poll


@router.post("/", response_model=PollResponse)
async def create_poll(
    poll_in: PollCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    poll = await crud.create_poll(session=session, poll_in=poll_in)
    return poll


@router.patch("/{poll_id}/", response_model=PollResponse)
async def update_poll(
    poll_id: uuid.UUID,
    poll_in: PollUpdate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    poll = await crud.update_poll(
        session=session,
        poll_id=poll_id,
        poll_in=poll_in,
    )

    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    return poll


@router.delete("/{poll_id}/")
async def delete_poll(
    poll_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_poll(session=session, poll_id=poll_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    return {"message": "success"}
