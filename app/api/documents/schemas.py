import uuid

from pydantic import BaseModel


class DocumentBase(BaseModel):
    file_url: str
    title: str
    is_active: bool


class DocumentResponse(DocumentBase):
    id: uuid.UUID
