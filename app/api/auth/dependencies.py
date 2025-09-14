from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Header, HTTPException, status

from core.config import settings
from api.auth.helpers import check_jwt, TOKEN_TYPE_REFRESH


async def get_refresh_token_payload(
    refresh_token: str = Header(alias=settings.header.refresh_token_header),
) -> str:
    try:
        payload = check_jwt(token=refresh_token)
        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a refresh token",
            )
        return payload

    except (ExpiredSignatureError, InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
