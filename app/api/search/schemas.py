import uuid
from datetime import date

from pydantic import BaseModel


class NewsResponseSearch(BaseModel):
    id: uuid.UUID
    image_url: str
    min_text: str
    news_date: date
