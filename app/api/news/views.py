from typing import Annotated
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Form, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from core.file.service import file_service, NEWS_FOLDER
from api.dependencies import get_current_active_user
from api.helpers import parse_str_to_date
from api.news.schemas import (
    NewsFullResponse,
    NewsPreviewResponse,
    NewsTypeCreate,
    NewsTypeResponse,
)
from api.news import crud

router = APIRouter()


@router.get("/", response_model=list[NewsFullResponse])
async def get_news(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news = await crud.get_news(session=session)
    return news


@router.get("/preview/", response_model=list[NewsPreviewResponse])
async def get_news_preview(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news = await crud.get_news(session=session)
    news_preview = []
    for news_item in news:
        news_preview.append(
            NewsPreviewResponse(
                id=news_item.id,
                image_url=news_item.image_url,
                min_text=news_item.min_text,
            )
        )

    return news_preview


@router.post("/", response_model=NewsFullResponse)
async def create_news(
    title: Annotated[str, Form()],
    body: Annotated[str, Form()],
    image: UploadFile,
    min_text: Annotated[str, Form()],
    news_date: Annotated[str, Form()],
    type_id: Annotated[uuid.UUID, Form()],
    keywords: Annotated[list[str], Form()],
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news_date = parse_str_to_date(news_date)
    image_url = await file_service.save_upload_file(
        upload_file=image, subdirectory=NEWS_FOLDER
    )
    news = await crud.create_news(
        session=session,
        title=title,
        body=body,
        keywords=keywords,
        image_url=image_url,
        min_text=min_text,
        news_date=news_date,
        type_id=type_id,
    )

    return news


@router.patch("/{news_id}/", response_model=NewsFullResponse)
async def update_news(
    news_id: uuid.UUID,
    title: Annotated[str | None, Form()] = None,
    body: Annotated[str | None, Form()] = None,
    keywords: Annotated[list[str] | None, Form()] = None,
    image: UploadFile | None = None,
    min_text: Annotated[str | None, Form()] = None,
    news_date: Annotated[str | None, Form()] = None,
    type_id: Annotated[uuid.UUID | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news_date = parse_str_to_date(news_date) if news_date else None
    current_news = await crud.get_news_by_id(session=session, news_id=news_id)
    if not current_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )

    if image:
        await file_service.delete_file(current_news.image_url)
        image_url = await file_service.save_upload_file(
            upload_file=image, subdirectory=NEWS_FOLDER
        )

    news = await crud.update_news(
        session=session,
        current_news=current_news,
        title=title,
        body=body,
        keywords=keywords,
        image_url=image_url,
        min_text=min_text,
        news_date=news_date,
        type_id=type_id,
    )

    return news


@router.delete("/{news_id}/")
async def delete_news(
    news_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_news(session=session, news_id=news_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )

    return {"message": "success"}


# ====================
# ====================
# ====================
# ====================
# ====================
# ====================


@router.get("/types/", response_model=list[NewsTypeResponse])
async def get_news_types(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_news_types(session=session)


@router.post("/types/", response_model=NewsTypeResponse)
async def create_news_type(
    type_in: NewsTypeCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news_type = await crud.create_news_type(session=session, type=type_in.type)
    if not news_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="News type already exists",
        )
    return news_type


@router.put("/types/{type_id}/", response_model=NewsTypeResponse)
async def update_news_type(
    type_id: uuid.UUID,
    type_in: NewsTypeCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news_type = await crud.update_news_type(
        session=session, type_id=type_id, type_name=type_in.type
    )
    if not news_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News type not found",
        )
    return news_type


@router.delete("/types/{type_id}/")
async def delete_news_type(
    type_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_news_type(session=session, type_id=type_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News type not found",
        )

    return {"message": "success"}
