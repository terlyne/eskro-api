import uuid

from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from api.auth.schemas import UserRegister
from api.users.schemas import UserUpdate
from api.users.helpers import is_valid_email


async def create_user(session: AsyncSession, user_in: UserRegister) -> User:
    user = User(**user_in.model_dump())
    session.add(user)
    await session.commit()
    # await session.refresh(user) # Не нужно обновлять юзера, т.к. данные нужные уже есть
    return user


async def get_user_and_validate_password(
    session: AsyncSession,
    username_or_email: str,
    password: str,
) -> User | None:
    user = await get_user_by_username_or_email(
        session=session,
        username_or_email=username_or_email,
    )

    if not user:
        return None

    if not user.check_password(password):
        return None

    return user


async def get_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> list[User]:
    stmt = select(User)

    if is_active:
        stmt = stmt.where(User.is_active == is_active)

    stmt = stmt.order_by(desc(User.created_at)).offset(skip).limit(limit)
    result = await session.scalars(stmt)
    users = result.all()

    return list(users)


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(statement=stmt)
    return user


async def get_user_by_username(
    session: AsyncSession,
    username: str,
) -> User | None:
    stmt = select(User).where(User.username == username)
    user = await session.scalar(statement=stmt)
    return user


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    stmt = select(User).where(User.email == email)
    user = await session.scalar(statement=stmt)
    return user


async def get_user_by_username_or_email(
    session: AsyncSession,
    username_or_email: str,
) -> User | None:
    if is_valid_email(username_or_email):
        return await get_user_by_email(session=session, email=username_or_email)

    return await get_user_by_username(session=session, username=username_or_email)


async def deactivate_user(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> bool:
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        return False

    user.is_active = False
    await session.commit()
    return True


async def activate_user(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> bool:
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        return False

    user.is_active = True
    await session.commit()
    return True


async def update_user(
    session: AsyncSession,
    user_update: UserUpdate,
) -> User:
    identifier = user_update.email or user_update.username
    user = await get_user_by_username_or_email(
        session=session, username_or_email=identifier
    )

    if user_update.email is not None:
        user.email = user_update.email
    if user_update.username is not None:
        user.username = user_update.username

    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> bool:
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        return False

    await session.delete(user)
    await session.commit()

    return True
