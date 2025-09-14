import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from core.email.service import email_service
from security import utils as security_utils
from api.dependencies import get_current_active_user
from api.subscribers.schemas import (
    SubscriberResponse,
    SubscriberCreate,
    NewsLetter,
)
from api.subscribers import crud


router = APIRouter()


@router.get("/", response_model=list[SubscriberResponse])
async def get_subscribers(
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    subscriber = await crud.get_subscribers(session=session)
    return subscriber


@router.post("/", response_model=SubscriberResponse)
async def subscribe_to_updates(
    type_id: uuid.UUID,
    subscriber_in: SubscriberCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    subscriber = await crud.create_subscriber(
        session=session, type_id=type_id, subscriber_in=subscriber_in
    )

    # Отправляем пользователю на почту подтверждение рассылки
    token = security_utils.encode_jwt(
        payload={
            "sub": str(subscriber.id),
        },
        expire_minutes=None,
    )
    await email_service.send_confirmation_subscription(
        email=subscriber_in.email, token=token
    )

    return subscriber


@router.post("/confirm/", response_model=SubscriberResponse)
async def confirm_subscription(
    token: str,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    payload = security_utils.decode_jwt(token=token)
    subscriber_id = payload["sub"]
    subscription = await crud.confirm_subscription(
        session=session, subscriber_id=subscriber_id
    )

    return subscription


@router.delete("/{subscriber_id}/")
async def delete_subscriber(
    subscriber_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):

    is_deleted = await crud.delete_subscriber(
        session=session, subscriber_id=subscriber_id
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found",
        )

    return {"message": "success"}


@router.post("/{type_id}/start-mailing/")
async def start_mailing_by_news_type(
    type_id: uuid.UUID,
    news_letter: NewsLetter,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    subscribers = await crud.get_subscribers_by_news_type_id(
        session=session, type_id=type_id
    )
    subscribers_emails = [subscriber.email for subscriber in subscribers]
    await email_service.mailing_to_subscribed(
        news_title=news_letter.title,
        news_text=news_letter.text,
        news_url=news_letter.news_url,
        emails=subscribers_emails,
    )
    return {"message": "success"}
