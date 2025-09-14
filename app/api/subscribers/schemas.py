from typing import Annotated
from datetime import date
import uuid

from pydantic import BaseModel, Field, EmailStr


class SubscriberBase(BaseModel):
    email: Annotated[EmailStr, Field(max_length=320)]
    subscribed_at: date
    is_confirmed: bool


class SubscriberResponse(SubscriberBase):
    id: uuid.UUID


class SubscriberCreate(SubscriberBase):
    subscribed_at: date | None = None
    is_confirmed: bool | None = None


class NewsLetter(BaseModel):
    title: str
    text: str
    news_url: str
