from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins.id import IdMixin


class Banner(Base, IdMixin):
    image_url: Mapped[str] = mapped_column(Text())
    redirect_url: Mapped[str] = mapped_column(
        Text()
    )  # URL при нажатии на который будет перенаправляться пользователь (URL страницы проекта)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    count_order: Mapped[int]  # Порядок отображения
