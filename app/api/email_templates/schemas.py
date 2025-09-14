from pydantic import BaseModel


class EmailTemplateResponse(BaseModel):
    body: str
    styles: str | None = None


class EmailTemplateUpdate(BaseModel):
    body: str | None = None
    styles: str | None = None
