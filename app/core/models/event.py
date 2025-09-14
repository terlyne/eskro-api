from datetime import datetime

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins.id import IdMixin


class Event(Base, IdMixin):
    title: Mapped[str] = mapped_column(Text())
    description: Mapped[str] = mapped_column(
        Text()
    )  # Описание мероприятия (не в формате HTML!)
    event_date: Mapped[datetime | None] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
    )
    location: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
    )  # Место проведения
