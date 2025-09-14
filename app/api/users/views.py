import uuid


from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from api.dependencies import get_current_active_user, get_current_admin
from api.users import crud
from api.users.schemas import UserResponse, UserResponseForAdmin, UserUpdate
from api.auth.schemas import UserChangePassword
from api.auth import crud as auth_crud


router = APIRouter()


@router.get("/me/", response_model=UserResponse)
async def get_user_info(
    user: User = Depends(get_current_active_user),
):
    return user


@router.patch("/me/", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await crud.update_user(session=session, user_update=user_update)
    return user


@router.get("/{user_id}/", response_model=UserResponseForAdmin)
async def get_user_by_id(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get("/", response_model=list[UserResponseForAdmin])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0),
    is_active: bool | None = None,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    users = await crud.get_users(
        session=session, skip=skip, limit=limit, is_active=is_active
    )
    return users


@router.delete("/{user_id}/deactivate/")
async def deactivate_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deactivated = await crud.deactivate_user(session=session, user_id=user_id)
    if not is_deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "success"}


@router.patch("/{user_id}/activate/")
async def activate_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_activated = await crud.activate_user(session=session, user_id=user_id)
    if not is_activated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "success"}


@router.post("/change-password/", response_model=UserResponse)
async def change_user_password(
    user_in: UserChangePassword,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        user = await auth_crud.change_user_password(
            session=session,
            user_id=user.id,
            password=user_in.password,
        )
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{user_id}/delete/")
async def delete_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_user(session=session, user_id=user_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "success"}
