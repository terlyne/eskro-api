import uuid

from pydantic import BaseModel


class BannerResponse(BaseModel):
    id: uuid.UUID
    image_url: str
    redirect_url: str
    is_active: bool
    count_order: int
