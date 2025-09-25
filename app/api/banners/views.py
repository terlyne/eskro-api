from typing import Annotated
import uuid

from fastapi import APIRouter, HTTPException, status, Form, UploadFile, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.file.service import file_service, BANNERS_IMAGES_FOLDER
from core.models import User
from core.db_helper import db_helper
from api.dependencies import get_current_active_user, verify_active_param_access
from api.banners.schemas import BannerResponse
from api.banners import crud

router = APIRouter()


@router.post("/", response_model=BannerResponse)
async def create_banner(
    image: UploadFile,
    redirect_url: Annotated[str, Form()],
    count_order: Annotated[int, Form(gt=0)],
    is_active: Annotated[bool, Form()] = True,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Сохраняем изображение баннера
    image_url = await file_service.save_file(
        upload_file=image,
        subdirectory=BANNERS_IMAGES_FOLDER,
    )

    banner = await crud.create_banner(
        session=session,
        image_url=image_url,
        redirect_url=redirect_url,
        is_active=is_active,
        count_order=count_order,
    )

    return banner


@router.get("/", response_model=list[BannerResponse])
async def get_banners(
    is_active: bool = Depends(verify_active_param_access),
    skip: int = Query(0, ge=0),
    limit: int = Query(6, ge=1),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    banners = await crud.get_banners(
        session=session,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return banners


@router.get("/{banner_id}/", response_model=BannerResponse)
async def get_banner_by_id(
    banner_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    banner = await crud.get_banner_by_id(session=session, banner_id=banner_id)
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found",
        )

    return banner


@router.patch("/{banner_id}/", response_model=BannerResponse)
async def update_banner(
    banner_id: uuid.UUID,
    image: UploadFile | None = None,
    redirect_url: Annotated[str | None, Form()] = None,
    count_order: Annotated[int | None, Form(gt=0)] = None,
    is_active: Annotated[bool | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_banner = await crud.get_banner_by_id(session=session, banner_id=banner_id)
    if not current_banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found",
        )

    if image:
        await file_service.delete_file(current_banner.image_url)
        image_url = await file_service.save_file(image, BANNERS_IMAGES_FOLDER)

    banner = await crud.update_banner(
        session=session,
        current_banner=current_banner,
        image_url=image_url,
        redirect_url=redirect_url,
        count_order=count_order,
        is_active=is_active,
    )

    return banner


@router.delete("/{banner_id}/")
async def delete_banner(
    banner_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_banner(session=session, banner_id=banner_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found",
        )

    return {"message": "success"}
