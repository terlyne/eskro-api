import re
from pathlib import Path
import aiofiles

from fastapi import HTTPException, status
from fastapi.templating import Jinja2Templates

from core.config import BASE_DIR
from api.email_templates.schemas import EmailTemplateResponse, EmailTemplateUpdate


EMAIL_TEMPLATES_DIR = BASE_DIR / "app" / "core" / "email" / "templates"

CHANGING_PASSWORD_TEMPLATE_NAME = "changing_password.html"
CONFIRMATION_REGISTER_TEMPLATE_NAME = "confirmation_register.html"
FEEDBACK_RESPONSE_TEMPLATE_NAME = "feedback_response.html"
REGISTER_INVITATION_TEMPLATE_NAME = "register_invitation.html"
CONFIRMATION_SUBSCRIPTION_TEMPLATE_NAME = "confirmation_register.html"
MAILING_TEMPLATE_NAME = "mailing.html"


class EmailTemplateService:
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.jinja_env = Jinja2Templates(directory=self.templates_dir)

    async def get_template_content(self, template_name: str) -> EmailTemplateResponse:
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_name}' not found",
            )

        if not template_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{template_name}' is not a file",
            )

        # Читаем контент шаблона
        async with aiofiles.open(template_path, "r", encoding="utf-8") as f:
            content = await f.read()

        styles = self._extract_styles(content)
        body = self._extract_body(content)

        return EmailTemplateResponse(
            body=body,
            styles=styles,
        )

    async def update_template_content(
        self, template_in: EmailTemplateUpdate, template_name: str
    ) -> EmailTemplateResponse:
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_name}' not found",
            )

        if not template_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{template_name}' is not a file",
            )

        # Читаем текущее содержимое шаблона
        async with aiofiles.open(template_path, "r", encoding="utf-8") as f:
            current_content = await f.read()
        # Обновляем содержимое шаблона
        updated_content = self._update_template_parts(
            current_content,
            template_in.body,
            template_in.styles,
        )

        # Сохраняем обновленный шаблон
        async with aiofiles.open(template_path, "w", encoding="utf-8") as f:
            await f.write(updated_content)

        # Возвращаем обновленный шаблон
        return EmailTemplateResponse(
            body=template_in.body or self._extract_body(current_content),
            styles=template_in.styles or self._extract_styles(current_content),
        )

    def _update_template_parts(
        self, current_content: str, new_body: str | None, new_styles: str | None
    ) -> str:
        content = current_content

        if new_body is not None:
            content = self._replace_block_content(content, "body", new_body)

        if new_styles is not None:
            styled_content = f"<style>\n{new_styles}\n</style>"
            content = self._replace_block_content(content, "style", styled_content)

        return content

    def _replace_block_content(
        self, content: str, block_name: str, new_content: str
    ) -> str:
        pattern = rf"({{%\s*block {block_name}\s*%}}).*?({{%\s*endblock\s*%}})"
        replacement = rf"\1\n{new_content}\n\2"

        if re.search(pattern, content, re.DOTALL):
            return re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            block_template = (
                f"{{% block {block_name} %}}\n{new_content}\n{{% endblock %}}"
            )
            return content + f"\n{block_template}"

    def _extract_styles(self, content: str):
        styles_pattern = r"{%\s*block style\s*%}(.*?){%\s*endblock\s*%}"
        style_match = re.search(styles_pattern, content, re.DOTALL)

        if style_match:
            style_content = style_match.group(1).strip()
            inner_style_pattern = r"<style>(.*?)</style>"
            inner_match = re.search(inner_style_pattern, style_content, re.DOTALL)
            if inner_match:
                return inner_match.group(1).strip()

        return None

    def _extract_body(self, content: str):
        body_pattern = r"{%\s*block body\s*%}(.*?){%\s*endblock\s*%}"
        body_match = re.search(body_pattern, content, re.DOTALL)

        if body_match:
            return body_match.group(1).strip()

        raise HTTPException(
            status_code=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found",
            )
        )


email_template_service = EmailTemplateService(EMAIL_TEMPLATES_DIR)
