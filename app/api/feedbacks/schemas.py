from typing import Annotated
import uuid

from pydantic import BaseModel, EmailStr, Field


class FeedbackBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: Annotated[EmailStr | None, Field(max_length=320)] = None
    message: str


class FeedbackResponse(FeedbackBase):
    id: uuid.UUID
    is_answered: bool
    response: str


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackAnswer(BaseModel):
    response: str
