from datetime import datetime
import uuid

from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Event


async def get_events(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 10,
) -> list[Event]:
    stmt = select(Event).offset(skip).limit(limit).order_by(desc(Event.created_at))
    result = await session.scalars(stmt)
    events = result.all()

    return list(events)


async def get_event_by_id(
    session: AsyncSession,
    event_id: uuid.UUID,
) -> Event | None:
    stmt = select(Event).where(Event.id == event_id)
    event = await session.scalar(stmt)

    return event


async def create_event(
    session: AsyncSession,
    title: str,
    description: str,
    image_url: str,
    is_active: bool,
    event_date: datetime | None = None,
    location: str | None = None,
) -> Event:
    event = Event(
        title=title,
        description=description,
        image_url=image_url,
        is_active=is_active,
        event_date=event_date,
        location=location,
    )

    session.add(event)
    await session.commit()
    await session.refresh(event)

    return event


async def update_event(
    session: AsyncSession,
    current_event: Event,
    **kw,
) -> Event:

    for field, value in kw.items():
        if hasattr(current_event, field) and value is not None:
            setattr(current_event, field, value)

    await session.commit()

    return current_event


async def delete_event(
    session: AsyncSession,
    event_id: uuid.UUID,
) -> bool:
    event = await get_event_by_id(session=session, event_id=event_id)
    if not event:
        return False

    await session.delete(event)
    await session.commit()

    return True
