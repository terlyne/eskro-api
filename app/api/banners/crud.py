import uuid

from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Banner


async def create_banner(
    session: AsyncSession,
    image_url: str,
    redirect_url: str,
    is_active: bool,
    count_order: int,
) -> Banner:
    banner = Banner(
        image_url=image_url,
        redirect_url=redirect_url,
        is_active=is_active,
        count_order=count_order,
    )

    await session.add(banner)
    await session.refresh(banner)
    return banner


async def get_banners(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 6,
) -> list[Banner]:
    stmt = select(Banner).offset(skip).limit(limit).order_by(desc(Banner.created_at))
    result = await session.scalars(stmt)
    banners = result.all()
    return list(banners)


async def get_banner_by_id(
    session: AsyncSession,
    banner_id: uuid.UUID,
) -> Banner | None:
    stmt = select(Banner).where(Banner.id == banner_id)
    banner = await session.scalar(stmt)

    return banner


async def update_banner(
    session: AsyncSession,
    current_banner: Banner,
    **kw,
) -> Banner | None:
    for field, value in kw.items():
        if value is not None and hasattr(current_banner, field):
            setattr(current_banner, field, value)

    await session.commit()

    return current_banner


async def delete_banner(
    session: AsyncSession,
    banner_id: uuid.UUID,
) -> bool:
    banner = await get_banner_by_id(session=session, banner_id=banner_id)
    if not banner:
        return False

    await session.delete(banner)
    await session.commit()

    return True
