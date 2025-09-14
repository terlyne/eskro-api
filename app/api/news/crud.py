import uuid
from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import News, NewsType


async def get_news(session: AsyncSession) -> list[News]:
    stmt = select(News).options(joinedload(News.type))
    result = await session.scalars(stmt)
    news = result.all()

    return list(news)


async def get_news_by_id(
    session: AsyncSession,
    news_id: uuid.UUID,
) -> News | None:
    stmt = select(News).options(joinedload(News.type)).where(News.id == news_id)
    news = await session.scalar(stmt)

    return news


async def create_news(
    session: AsyncSession,
    title: str,
    body: str,
    keywords: list[str],
    image_url: str,
    min_text: str,
    news_date: date,
    type_id: uuid.UUID,
) -> News:
    news = News(
        title=title,
        body=body,
        keywords=keywords,
        image_url=image_url,
        min_text=min_text,
        news_date=news_date,
        type_id=type_id,
    )

    session.add(news)
    await session.commit()
    await session.refresh(news)
    return news


async def update_news(
    session: AsyncSession,
    current_news: News,
    **kw,
) -> News | None:
    for field, value in kw.items():
        if hasattr(current_news, field) and value is not None:
            setattr(current_news, field, value)

    await session.commit()
    await session.refresh(current_news)

    return current_news


async def delete_news(
    session: AsyncSession,
    news_id: uuid.UUID,
) -> bool:
    news = await get_news_by_id(session=session, news_id=news_id)
    if not news:
        return False

    await session.delete(news)
    await session.commit()

    return True


async def get_news_type(
    session: AsyncSession,
    type: str,
) -> NewsType | None:
    stmt = select(NewsType).where(NewsType.type == type)
    subscription_type = await session.scalar(stmt)

    return subscription_type


async def create_news_type(session: AsyncSession, type: str) -> NewsType | None:
    news_type = await get_news_type(session=session, type=type)
    if news_type:
        return None

    news_type = NewsType(type=type)
    session.add(news_type)
    await session.commit()
    await session.refresh(news_type)

    return news_type


async def get_news_types(
    session: AsyncSession,
) -> list[NewsType]:
    stmt = select(NewsType).order_by(NewsType.type)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_news_type_by_id(
    session: AsyncSession,
    type_id: uuid.UUID,
) -> NewsType | None:
    return await session.get(NewsType, type_id)


async def update_news_type(
    session: AsyncSession,
    type_id: uuid.UUID,
    type_name: str,
) -> NewsType | None:
    news_type = await get_news_type_by_id(session, type_id)
    if not news_type:
        return None

    news_type.type = type_name
    await session.commit()
    await session.refresh(news_type)
    return news_type


async def delete_news_type(
    session: AsyncSession,
    type_id: uuid.UUID,
) -> bool:
    news_type = await get_news_type_by_id(session, type_id)
    if not news_type:
        return False

    await session.delete(news_type)
    await session.commit()
    return True
