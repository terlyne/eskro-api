from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins.id import IdMixin
from core.models.poll_question import PollQuestion

if TYPE_CHECKING:
    from core.models.poll_question import PollQuestion


class Poll(Base, IdMixin):
    theme: Mapped[str] = mapped_column(String(100))  # Тема опроса
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

    questions: Mapped[list["PollQuestion"]] = relationship(back_populates="poll")
