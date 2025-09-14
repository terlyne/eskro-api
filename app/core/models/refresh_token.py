from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from core.models.user import User


class RefreshToken(Base):
    # __mapper_args__ = {"exclude_properties": ["id"]}
    __tablename__ = "refresh_tokens"

    jti: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
    )  # Поле, которое устанавливает токену ID (нет смысла добавлять еще какие-то поля, потому что при проверке токена функция парсящая этот токен выдаст ошибку)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    # Информация об устройстве для выявления аномалий работы с refresh токеном
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )  # Дата истечения срока действия токена
    is_revoked: Mapped[bool] = mapped_column(
        default=False, server_default="false"
    )  # Отозван токен или нет (при логауте пользователя отзываем токен, или если произошла аномалия)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
