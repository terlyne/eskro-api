from typing import TYPE_CHECKING
import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins.id import IdMixin

if TYPE_CHECKING:
    from core.models.poll_question import PollQuestion


class PollAnswer(Base, IdMixin):
    __tablename__ = "poll_answers"

    answer_text: Mapped[str] = mapped_column(Text())  # Текст ответа

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("poll_questions.id"))
    question: Mapped["PollQuestion"] = relationship(back_populates="answers")
