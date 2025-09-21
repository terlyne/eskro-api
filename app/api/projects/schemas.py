from typing import Annotated
import uuid

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    title: str
    body: str
    is_active: bool
    min_text: str
    image_url: str
    keywords: list[str]
    theme: str
    category: str


class ProjectPreviewResponse(BaseModel):
    id: uuid.UUID
    min_text: str
    image_url: str


class ProjectFullResponse(ProjectBase):
    id: uuid.UUID
