import uuid
from datetime import datetime

from pydantic import BaseModel


class EventResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    event_date: datetime | None = None
    image_url: str
    is_active: bool
    location: str | None = None
