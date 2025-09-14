from typing import Annotated
import uuid
from datetime import date

from pydantic import BaseModel, Field


class NewsBase(BaseModel):
    title: str
    body: str
    keywords: list[str]
    image_url: str
    min_text: str
    news_date: date
    type_id: uuid.UUID


class NewsFullResponse(NewsBase):
    id: uuid.UUID


class NewsPreviewResponse(BaseModel):
    id: uuid.UUID
    image_url: str
    min_text: str


class NewsTypeBase(BaseModel):
    type: Annotated[str, Field(max_length=100)]


class NewsTypeResponse(NewsTypeBase):
    id: uuid.UUID


class NewsTypeCreate(NewsTypeBase):
    pass
