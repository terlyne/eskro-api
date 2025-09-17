import uuid
from datetime import datetime, timezone, timedelta

from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db_helper import db_helper
from core.email.service import email_service
from core.models import User
from api.auth.helpers import (
    create_jwt_without_type,
    create_jwt,
    check_jwt,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
)
from api.auth import crud
from api.dependencies import get_current_admin
from api.users import crud as users_crud
from api.users.schemas import UserResponse
from api.auth.schemas import (
    UserRegister,
    UserChangePassword,
    TokenInfo,
    RefreshTokenCreate,
)
from api.auth.dependencies import (
    get_refresh_token_payload,
)

router = APIRouter()


@router.get("/get-public-key/")
async def get_public_key():
    public_key = settings.auth.public_key_path.read_text()
    return {"public_key": public_key}


@router.post("/register/", response_model=UserResponse)
async def register_user(
    token: str,
    user_in: UserRegister,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        # Проверяем токен в URL
        check_jwt(token=token)

        user = await crud.register_user(session=session, user_in=user_in)

        token_register_confirmation = create_jwt_without_type(
            payload={"sub": str(user.id)}
        )

        # Отправляем письмо на почту для подтверждения регистрации пользователем
        await email_service.send_confirmation_register_email(
            email=user.email, token=token_register_confirmation, username=user.username
        )

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


@router.post("/send-register-invitation/")
async def send_register_invitation(
    email: str,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_user_exists = (
        True
        if await users_crud.get_user_by_email(session=session, email=email)
        else False
    )

    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    register_invitation_token = create_jwt_without_type(
        payload={"email": email},
    )

    await email_service.send_register_invitation(
        email=email, token=register_invitation_token
    )


@router.post("/confirm-registration/")
async def confirm_user_registration(
    token: str,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        user_id = check_jwt(token=token)["sub"]
        await crud.confirm_registration(session=session, user_id=user_id)

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


@router.post("/login/", response_model=TokenInfo)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )

    #  Логиним пользователя
    user = await crud.login_user(
        session=session,
        username_or_email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise unauthorized_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not active",
        )

    # Выпускаем новые access и refresh токены
    access_token = create_jwt(
        payload={
            "sub": str(user.id),
        },
        token_type=TOKEN_TYPE_ACCESS,
    )
    refresh_token_jti = uuid.uuid4()

    refresh_token = create_jwt(
        payload={
            "sub": str(user.id),
            "jti": str(refresh_token_jti),
        },
        token_type=TOKEN_TYPE_REFRESH,
        expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days),
    )
    # Собираем данные с Request для сохранения refresh токена в БД
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host

    # Добавляем refresh токен в БД
    await crud.add_refresh_token(
        session=session,
        token=RefreshTokenCreate(
            jti=refresh_token_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.auth.refresh_token_expire_days),
        ),
        user_id=user.id,
    )

    token_info = TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    return token_info


@router.post("/refresh/")
async def refresh_tokens(
    request: Request,
    refresh_token_payload: dict = Depends(get_refresh_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    jti = refresh_token_payload["jti"]
    user_id = refresh_token_payload["sub"]

    # Получаем токен из БД
    refresh_token_from_db = await crud.get_refresh_token(session=session, jti=jti)

    if not refresh_token_from_db or refresh_token_from_db.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
        )

    # Проверяем аномалии
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host

    if (
        refresh_token_from_db.user_agent != user_agent
        or refresh_token_from_db.ip_address != ip_address
    ):

        # Отзываем из-за аномалии
        await crud.revoke_refresh_token(session, jti)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Suspicious activity detected",
        )

    # Получаем пользователя
    user = await users_crud.get_user_by_id(session=session, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Отзываем старый токен (после всех проверок)
    await crud.revoke_refresh_token(session=session, jti=jti)

    # Выпускаем новые access и refresh токены
    access_token = create_jwt(
        payload={
            "sub": str(user.id),
        },
        token_type=TOKEN_TYPE_ACCESS,
    )
    refresh_token_jti = uuid.uuid4()

    refresh_token = create_jwt(
        payload={
            "sub": str(user.id),
            "jti": str(refresh_token_jti),
        },
        token_type=TOKEN_TYPE_REFRESH,
        expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days),
    )
    # Собираем данные с Request для сохранения refresh токена в БД
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host

    # Добавляем refresh токен в БД
    await crud.add_refresh_token(
        session=session,
        token=RefreshTokenCreate(
            jti=refresh_token_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.auth.refresh_token_expire_days),
        ),
        user_id=user.id,
    )

    token_info = TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    return token_info


@router.post("/logout/")
async def logout_device(
    refresh_token_payload: str = Depends(get_refresh_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    jti = refresh_token_payload["jti"]
    await crud.revoke_refresh_token(session=session, jti=jti)


@router.post("/logout-all/")
async def logout_all_devices(
    refresh_token_payload: str = Depends(get_refresh_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user_id = refresh_token_payload["sub"]
    await crud.revoke_refresh_tokens(session=session, user_id=user_id)


@router.post("/change-password/")
async def change_password(
    email: str,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await users_crud.get_user_by_email(session=session, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or inactive",
        )

    token = create_jwt_without_type(
        payload={
            "sub": str(user.id),
            "email": user.email,
        },
        expire_minutes=settings.auth.changing_password_token_expire_minutes,
    )

    await email_service.send_changing_password_url(
        email=user.email,
        token=token,
    )


@router.post("/confirm-changing-password/", response_model=UserResponse)
async def confirm_changing_password(
    token: str,
    user_in: UserChangePassword,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        payload = check_jwt(token=token)
        user_id = payload["sub"]

        user = await crud.change_user_password(
            session=session, user_id=user_id, password=user_in.password
        )
        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change token expired",
        )
    except (InvalidTokenError, ValueError) as e:
        if str(e) == "New password cannot be the same as the old one":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
