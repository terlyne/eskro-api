from typing import Annotated
import uuid

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    title: str
    body: str
    is_active: bool
    keywords: list[Annotated[str, Field(max_length=100)]]
    theme: str
    category: Annotated[str, Field(max_length=100)]


class ProjectResponse(ProjectBase):
    id: uuid.UUID


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    is_active: bool | None = None
    keywords: list[Annotated[str, Field(max_length=100)]] | None = None
    theme: str | None = None
    category: Annotated[str, Field(max_length=100)] | None = None
