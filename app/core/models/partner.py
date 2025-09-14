from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base
from core.models.mixins.id import IdMixin


class Partner(Base, IdMixin):
    logo_url: Mapped[str] = mapped_column(Text())
    partner_name: Mapped[str] = mapped_column(Text())
    partner_url: Mapped[str | None] = mapped_column(
        Text(), nullable=True
    )  # URL сайта партнера
    count_order: Mapped[int]  # Порядок отображения
