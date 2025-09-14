from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from core.models.user import User, ADMIN_ROLE
from core.db_helper import db_helper
from api.users.crud import get_user_by_id
from security import utils as security_utils

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login/",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    try:
        payload = security_utils.decode_jwt(token=token)
        user_id = payload["sub"]
        user = await get_user_by_id(session=session, user_id=user_id)
        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation token expired",
        )
    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not active",
        )

    return user


async def get_current_admin(
    user: User = Depends(get_current_active_user),
):
    if user.role != ADMIN_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    return user
