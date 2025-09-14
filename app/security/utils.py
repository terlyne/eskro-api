from typing import Any
from datetime import datetime, timedelta, timezone

import jwt
import bcrypt

from core.config import settings


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password=password.encode(),
        salt=salt,
    )


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int | None = settings.auth.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)

    if expire_timedelta:
        expire = now + expire_timedelta
        to_encode.update(
            exp=expire,
            iat=now,
        )
    elif expire_minutes:
        expire = now + timedelta(minutes=expire_minutes)
        to_encode.update(
            exp=expire,
            iat=now,
        )

    encoded = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )

    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth.public_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
) -> Any:
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )

    return decoded
