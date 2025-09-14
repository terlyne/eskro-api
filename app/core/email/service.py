from jinja2 import Environment, FileSystemLoader
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema

from core.config import settings, BASE_DIR


class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.email.username,
            MAIL_PASSWORD=settings.email.password,
            MAIL_FROM=settings.email.mail_from,
            MAIL_FROM_NAME=settings.email.mail_from_name,
            MAIL_PORT=settings.email.port,
            MAIL_SERVER=settings.email.server,
            MAIL_STARTTLS=settings.email.starttls,
            MAIL_SSL_TLS=settings.email.ssl_tls,
            USE_CREDENTIALS=settings.email.use_credentials,
        )
        self.fast_mail = FastMail(self.config)
        self.templates_path = BASE_DIR / "app" / "core" / "email" / "templates"
        self.env = Environment(
            loader=FileSystemLoader(self.templates_path),
            autoescape=True,
            auto_reload=True,  # False для prod'а, True для dev'а
        )

    async def send_confirmation_register_email(
        self, email: str, token: str, username: str
    ):
        template = self.env.get_template("confrim_registration.html")

        html_content = template.render(
            username=username,
            confirmation_url=f"{settings.frontend.confirmation_register_url}/?token={token}",
        )

        message = MessageSchema(
            subject="Подтверждение регистрации",
            recipients=[email],
            body=html_content,
            subtype="html",
        )

        await self.fast_mail.send_message(message)

    async def send_register_invitation(self, email: str, token: str):
        template = self.env.get_template("register_invitation.html")

        html_content = template.render(
            invitation_url=f"{settings.frontend.register_invitation_url}/?token={token}"
        )

        message = MessageSchema(
            subject="Приглашение на регистрацию",
            recipients=[email],
            body=html_content,
            subtype="html",
        )

        await self.fast_mail.send_message(message)

    async def send_changing_password_url(self, email: str, token: str):
        template = self.env.get_template("changing_password.html")

        html_content = template.render(
            changing_password_url=f"{settings.frontend.changing_password_url}/?token={token}"
        )

        message = MessageSchema(
            subject="Изменение пароля",
            recipients=[email],
            body=html_content,
            subtype="html",
        )

        await self.fast_mail.send_message(message)

    async def send_response_to_feedback(
        self,
        email: str,
        first_name: str,
        middle_name: str,
        question: str,
        response: str,
    ):
        template = self.env.get_template("feedback_response.html")

        html_content = template.render(
            first_name=first_name,
            middle_name=middle_name,
            question=question,
            response=response,
        )

        message = MessageSchema(
            subject="Ответ на вопрос",
            recipients=[email],
            body=html_content,
            subtype="html",
        )

        await self.fast_mail.send_message(message)

    async def send_confirmation_subscription(self, email: str, token: str):
        template = self.env.get_template("confirmation_subscription.html")

        html_content = template.render(
            confirmation_url=f"{settings.frontend.subscription_confirmation_url}/?token={token}",
        )

        message = MessageSchema(
            subject="Подтверждение рассылки",
            recipients=[email],
            body=html_content,
            subtype="html",
        )

        await self.fast_mail.send_message(message)

    async def mailing_to_subscribed(
        self,
        news_title: str,
        news_text: str,
        news_url: str,
        *emails: str,
    ):
        template = self.env.get_template("mailing.html")

        html_content = template.render(
            title=news_title,
            text=news_text,
            redirect_url=news_url,
        )

        message = MessageSchema(
            subject="Новая новость",
            recipients=[*emails],
            body=html_content,
            subtype="html",
        )

        await self.fast_mail.send_message(message)


email_service = EmailService()
