import uuid

from pydantic import BaseModel


class PartnerResponse(BaseModel):
    id: uuid.UUID
    logo_url: str
    partner_name: str
    partner_url: str | None = None
    count_order: int
