from typing import Annotated
import uuid

from pydantic import BaseModel, Field


class PollBase(BaseModel):
    theme: Annotated[str, Field(max_length=100)]
    is_active: bool


class PollCreate(PollBase):
    pass


class PollUpdate(BaseModel):
    theme: Annotated[str | None, Field(max_length=100)] = None
    is_active: bool | None = None


class QuestionBase(BaseModel):
    question_text: str


class QuestionCreate(QuestionBase):
    pass


class AnswerBase(BaseModel):
    answer_text: str


class AnswerResponse(AnswerBase):
    id: uuid.UUID


class AnswerCreate(AnswerBase):
    pass


class QuestionResponse(QuestionBase):
    id: uuid.UUID
    answers: list[AnswerResponse] = []


class PollResponse(PollBase):
    id: uuid.UUID
    questions: list[QuestionResponse] = []
