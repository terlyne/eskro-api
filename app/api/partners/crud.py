import uuid

from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Partner


async def get_partners(session: AsyncSession) -> list[Partner]:
    stmt = select(Partner).order_by(desc(Partner.count_order))
    result = await session.scalars(stmt)
    partners = result.all()

    return list(partners)


async def get_partner_by_id(
    session: AsyncSession,
    partner_id: uuid.UUID,
) -> Partner | None:
    stmt = select(Partner).where(Partner.id == partner_id)
    partner = await session.scalar(stmt)

    return partner


async def create_partner(
    session: AsyncSession,
    logo_url: str,
    partner_name: str,
    count_order: int,
    partner_url: str | None = None,
) -> Partner:
    partner = Partner(
        logo_url=logo_url,
        partner_name=partner_name,
        count_order=count_order,
        partner_url=partner_url,
    )

    session.add(partner)
    await session.commit()
    await session.refresh(partner)

    return partner


async def update_partner(
    session: AsyncSession,
    current_partner: Partner,
    **kw,
) -> Partner | None:
    for field, value in kw.items():
        if hasattr(current_partner, field) and value is not None:
            setattr(current_partner, field, value)

    await session.commit()

    return current_partner


async def delete_partner(
    session: AsyncSession,
    partner_id: uuid.UUID,
):
    partner = await get_partner_by_id(session=session, partner_id=partner_id)
    if not partner:
        return False

    await session.delete(partner)
    await session.commit()

    return True
