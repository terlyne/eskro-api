from typing import Annotated
import uuid

from pydantic import BaseModel, Field


class PollBase(BaseModel):
    theme: Annotated[str, Field(max_length=100)]
    yandex_poll_url: str
    is_active: bool


class PollResponse(PollBase):
    id: uuid.UUID


class PollCreate(PollBase):
    pass


class PollUpdate(BaseModel):
    theme: str | None = None
    yandex_poll_url: str | None = None
    is_active: bool | None = None
