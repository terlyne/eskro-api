import string
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models.user import User, ADMIN_ROLE
from core.email.service import email_service
from api.auth.helpers import create_jwt_without_type


class AdminService:
    async def create_admin(self, session: AsyncSession) -> bool:
        # Проверяем, не существует ли уже админ
        exisiting_admin = await session.scalar(
            select(User).where(User.role == ADMIN_ROLE)
        )

        if exisiting_admin:
            return False

        admin = User(
            email=settings.admin.email,
            username=settings.admin.username,
            # password=self._generate_random_password(), change from deploy
            password="adminadmin",
            role=ADMIN_ROLE,
            # is_active=False,  # Администратор при запуске приложения не активен # change from deply
            is_active=True,
        )

        session.add(admin)
        await session.commit()

        # Отправляем администратору сообщение на почту для подтверждение регистрации
        payload = {"email": admin.email}
        register_invitation_token = create_jwt_without_type(payload=payload)
        await email_service.send_register_invitation(
            email=admin.email,
            token=register_invitation_token,
        )

    def _generate_random_password(self, length: int = 16) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))


admin_service = AdminService()
