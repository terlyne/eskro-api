import uuid

from sqlalchemy import select, desc, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Subscriber, NewsType
from api.subscribers.schemas import SubscriberCreate
from api.news.crud import get_news_type_by_id


async def get_subscribers(
    session: AsyncSession,
) -> list[Subscriber]:
    stmt = (
        select(Subscriber)
        .options(joinedload(Subscriber.type))
        .order_by(desc(Subscriber.created_at))
    )
    result = await session.scalars(stmt)
    subscribers = result.all()

    return list(subscribers)


async def get_subscribers_by_news_type_id(
    session: AsyncSession,
    type_id: uuid.UUID,
) -> list[Subscriber] | None:
    news_type = await get_news_type_by_id(session=session, type_id=type_id)
    if not news_type:
        return None

    stmt = (
        select(Subscriber)
        .joinedload(Subscriber.type)
        .where(Subscriber.type_id == type_id)
    )
    result = await session.scalars(stmt)
    subscribers = result.all()

    return list(subscribers)


async def get_subscriber_by_id(
    session: AsyncSession,
    subscriber_id: uuid.UUID,
) -> Subscriber | None:
    stmt = (
        select(Subscriber)
        .options(joinedload(Subscriber.type))
        .where(Subscriber.id == subscriber_id)
    )
    subscriber = await session.scalar(stmt)

    return subscriber


async def create_subscriber(
    session: AsyncSession,
    type_id: uuid.UUID,
    subscriber_in: SubscriberCreate,
) -> Subscriber:
    subscriber = Subscriber(
        **subscriber_in.model_dump(exclude_none=True),
        type_id=type_id,
    )
    session.add(subscriber)

    await session.commit()
    await session.refresh(subscriber)

    return subscriber


async def confirm_subscription(
    session: AsyncSession,
    subscriber_id: uuid.UUID,
) -> Subscriber:
    subscriber = await get_subscriber_by_id(
        session=session, subscriber_id=subscriber_id
    )
    subscriber.is_confirmed = True
    await session.commit()

    return subscriber


async def delete_subscriber(
    session: AsyncSession,
    subscriber_id: uuid.UUID,
) -> bool:
    subscriber = await get_subscriber_by_id(
        session=session, subscriber_id=subscriber_id
    )
    if not subscriber:
        return False

    await session.delete(subscriber)
    await session.commit()

    return True
