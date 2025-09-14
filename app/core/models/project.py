from sqlalchemy import Text, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins.id import IdMixin


class Project(Base, IdMixin):
    title: Mapped[str] = mapped_column(Text())
    body: Mapped[str] = mapped_column(Text())  # Содержание проекта в формате HTML
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

    # Ключевые слова для поиска внутри сайта
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String(100)))

    # Тематика (образование, воспитание, профориентация)
    theme: Mapped[str] = mapped_column(String(100))

    # Категория (для родителей, для учителей, нормативы)
    category: Mapped[str] = mapped_column(String(100))
