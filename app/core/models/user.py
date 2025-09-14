from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins.id import IdMixin
from security.utils import hash_password, validate_password

if TYPE_CHECKING:
    from app.core.models.refresh_token import RefreshToken

ADMIN_ROLE = "admin"
USER_ROLE = "user"


class User(Base, IdMixin):
    email: Mapped[str] = mapped_column(String(320), unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    role: Mapped[str] = mapped_column(
        String(20),
        default=USER_ROLE,
        server_default=USER_ROLE,
    )
    _hashed_password: Mapped[bytes] = mapped_column("hashed_password")
    is_active: Mapped[bool] = mapped_column(default=False, server_default="false")

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        email: str,
        username: str,
        password: str,
        role: str = USER_ROLE,
        is_active: bool = False,
    ):
        super().__init__(
            email=email,
            username=username,
            password=password,
            role=role,
            is_active=is_active,
        )
        self.password = password

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        self._hashed_password = hash_password(password=plain_password)

    def check_password(self, plain_password: str) -> bool:
        return validate_password(
            password=plain_password, hashed_password=self._hashed_password
        )
