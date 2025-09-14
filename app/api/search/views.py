from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from api.search import crud
from api.search.schemas import NewsResponseSearch

router = APIRouter()


@router.get("/news/suggestions/")
async def get_news_suggestions(
    query: str = Query(min_length=1),
    limit: int = Query(5, ge=1, le=10),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    suggestions = await crud.get_suggestions(session=session, query=query, limit=limit)
    return {"suggestions": suggestions}


@router.get("/news/", response_model=list[NewsResponseSearch])
async def get_news_by_query(
    query: str = Query(min_length=1),
    limit: int = Query(5, ge=1),
    skip: int = Query(0, ge=0),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    news_items = await crud.search_news(
        session=session,
        query=query,
        limit=limit,
        skip=skip,
    )

    # Преобразуем в схему ответа
    return [
        NewsResponseSearch(
            id=news.id,
            image_url=news.image_url,
            min_text=news.min_text,
            news_date=news.news_date,
        )
        for news in news_items
    ]
