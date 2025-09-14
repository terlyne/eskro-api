from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins.id import IdMixin


if TYPE_CHECKING:
    from core.models.subscriber import Subscriber
    from core.models.news import News


class NewsType(Base, IdMixin):
    __tablename__ = "news_types"
    type: Mapped[str] = mapped_column(String(100))
    subscribers: Mapped[list["Subscriber"]] = relationship(back_populates="type")
    news: Mapped[list["News"]] = relationship(back_populates="type")
