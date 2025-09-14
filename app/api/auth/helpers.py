from datetime import timedelta

from core.config import settings
from security import utils as security_utils


TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def create_jwt_without_type(
    payload: dict,
    private_key: str = settings.auth.private_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.registration_token_expire_minutes,
):
    return security_utils.encode_jwt(
        payload=payload,
        private_key=private_key,
        algorithm=algorithm,
        expire_minutes=expire_minutes,
    )


def create_jwt(
    token_type: str,
    payload: dict,
    private_key: str = settings.auth.private_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    to_encode.update(
        type=token_type,
    )

    return security_utils.encode_jwt(
        payload=to_encode,
        private_key=private_key,
        algorithm=algorithm,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def check_jwt(
    token: str | bytes,
    public_key: str = settings.auth.public_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
):
    return security_utils.decode_jwt(
        token=token,
        public_key=public_key,
        algorithm=algorithm,
    )
