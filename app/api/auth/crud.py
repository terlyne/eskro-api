import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, RefreshToken
from security.utils import validate_password
from api.auth.schemas import UserRegister, RefreshTokenCreate
from api.users import crud as users_crud


async def register_user(session: AsyncSession, user_in: UserRegister) -> User:
    user = await users_crud.create_user(session=session, user_in=user_in)
    return user


async def login_user(
    session: AsyncSession, username_or_email: str, password: str
) -> User | None:
    user = await users_crud.get_user_and_validate_password(
        session=session,
        username_or_email=username_or_email,
        password=password,
    )
    if not user.is_active:
        return None
    return user


async def confirm_registration(session: AsyncSession, user_id: uuid.UUID) -> bool:
    user = await users_crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        return False
    user.is_active = True
    await session.commit()
    # await session.refresh(user)
    return True


async def add_refresh_token(
    session: AsyncSession,
    token: RefreshTokenCreate,
    user_id: uuid.UUID,
) -> RefreshToken:
    refresh_token = RefreshToken(**token.model_dump(), user_id=user_id)
    session.add(refresh_token)
    await session.commit()
    return token


async def get_refresh_token(
    session: AsyncSession,
    jti: uuid.UUID,
) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.jti == jti)
    token = await session.scalar(statement=stmt)
    return token


async def revoke_refresh_tokens(
    session: AsyncSession,
    user_id: uuid.UUID,
):
    stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
    result = list(await session.scalars(statement=stmt))

    refresh_tokens: list[RefreshToken] = result.all()

    for token in refresh_tokens:
        token.is_revoked = False

    await session.commit()


async def revoke_refresh_token(
    session: AsyncSession,
    jti: uuid.UUID,
):
    token = await get_refresh_token(session=session, jti=jti)
    token.is_revoked = True
    await session.commit()


async def change_user_password(
    session: AsyncSession, user_id: uuid.UUID, password: str
):
    user = await users_crud.get_user_by_id(session=session, user_id=user_id)

    if user.check_password(plain_password=password):
        raise ValueError("New password cannot be the same as the old one")

    user.password = password
    await session.commit()
    await session.refresh(user)
    return user
