import uuid

from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Poll
from api.polls.schemas import PollCreate, PollUpdate


async def get_polls(session: AsyncSession) -> list[Poll]:
    stmt = select(Poll).order_by(desc(Poll.created_at))
    result = await session.scalars(stmt)
    polls = result.all()

    return list(polls)


async def get_poll_by_id(
    session: AsyncSession,
    poll_id: uuid.UUID,
) -> Poll | None:
    stmt = select(Poll).where(Poll.id == poll_id)
    poll = await session.scalar(stmt)

    return poll


async def create_poll(
    session: AsyncSession,
    poll_in: PollCreate,
) -> Poll:
    poll = Poll(**poll_in.model_dump())
    session.add(poll)
    await session.commit()
    await session.refresh(poll)

    return poll


async def update_poll(
    session: AsyncSession,
    poll_id: uuid.UUID,
    poll_in: PollUpdate,
) -> Poll | None:
    poll = await get_poll_by_id(session=session, poll_id=poll_id)
    if not poll:
        return None

    update_data = poll_in.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(poll, field, value)

    await session.commit()
    await session.refresh(poll)

    return poll


async def delete_poll(
    session: AsyncSession,
    poll_id: uuid.UUID,
) -> bool:
    poll = await get_poll_by_id(session=session, poll_id=poll_id)
    if not poll:
        return False

    await session.delete(poll)
    await session.commit()

    return True
