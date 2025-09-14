import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: Annotated[EmailStr, Field(max_length=320)]
    username: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=8)]


class UserChangePassword(BaseModel):
    password: Annotated[str, Field(min_length=8)]


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class RefreshTokenCreate(BaseModel):
    jti: uuid.UUID
    user_agent: str | None = None
    ip_address: str | None = None
    expires_at: datetime
    is_revoked: bool = False
