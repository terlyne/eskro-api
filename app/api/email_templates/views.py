from fastapi import APIRouter, Depends

from core.models import User
from core.email.template_service import (
    email_template_service,
    CHANGING_PASSWORD_TEMPLATE_NAME,
    CONFIRMATION_REGISTER_TEMPLATE_NAME,
    FEEDBACK_RESPONSE_TEMPLATE_NAME,
    REGISTER_INVITATION_TEMPLATE_NAME,
    CONFIRMATION_SUBSCRIPTION_TEMPLATE_NAME,
    MAILING_TEMPLATE_NAME,
)
from api.dependencies import get_current_active_user
from api.email_templates.schemas import EmailTemplateUpdate

router = APIRouter()


@router.get("/changing-password/")
async def get_changing_password_template(
    user: User = Depends(get_current_active_user),
):
    template_content = await email_template_service.get_template_content(
        CHANGING_PASSWORD_TEMPLATE_NAME,
    )

    return template_content


@router.get("/confirmation_register/")
async def get_confirmation_register_template(
    user: User = Depends(get_current_active_user),
):
    template_content = await email_template_service.get_template_content(
        CONFIRMATION_REGISTER_TEMPLATE_NAME,
    )

    return template_content


@router.get("/feedback-response/")
async def get_feedback_response_template(
    user: User = Depends(get_current_active_user),
):
    template_content = await email_template_service.get_template_content(
        FEEDBACK_RESPONSE_TEMPLATE_NAME,
    )

    return template_content


@router.get("/register-invitation/")
async def get_register_invitation_template(
    user: User = Depends(get_current_active_user),
):
    template_content = await email_template_service.get_template_content(
        REGISTER_INVITATION_TEMPLATE_NAME,
    )

    return template_content


@router.get("/confirmation-subscription/")
async def get_confirmation_subscription_template(
    user: User = Depends(get_current_active_user),
):
    template_content = await email_template_service.get_template_content(
        CONFIRMATION_SUBSCRIPTION_TEMPLATE_NAME,
    )

    return template_content


@router.get("/mailing/")
async def get_mailing_template(
    user: User = Depends(get_current_active_user),
):
    template_content = await email_template_service.get_template_content(
        MAILING_TEMPLATE_NAME,
    )

    return template_content


@router.patch("/changing-password/")
async def update_changing_password_template(
    template_in: EmailTemplateUpdate,
    user: User = Depends(get_current_active_user),
):
    new_template = await email_template_service.update_template_content(
        template_in, template_name=CHANGING_PASSWORD_TEMPLATE_NAME
    )
    return new_template


@router.patch("/confirmation_register/")
async def update_confirmation_register_template(
    template_in: EmailTemplateUpdate,
    user: User = Depends(get_current_active_user),
):
    new_template = await email_template_service.update_template_content(
        template_in, template_name=CONFIRMATION_REGISTER_TEMPLATE_NAME
    )
    return new_template


@router.patch("/feedback-response/")
async def update_feedback_response_template(
    template_in: EmailTemplateUpdate,
    user: User = Depends(get_current_active_user),
):
    new_template = await email_template_service.update_template_content(
        template_in, template_name=FEEDBACK_RESPONSE_TEMPLATE_NAME
    )
    return new_template


@router.patch("/register-invitation/")
async def update_register_invitation_template(
    template_in: EmailTemplateUpdate,
    user: User = Depends(get_current_active_user),
):
    new_template = await email_template_service.update_template_content(
        template_in, template_name=REGISTER_INVITATION_TEMPLATE_NAME
    )
    return new_template


@router.patch("/confirmation-subscription/")
async def update_confirmation_subscription_template(
    template_in: EmailTemplateUpdate,
    user: User = Depends(get_current_active_user),
):
    new_template = await email_template_service.update_template_content(
        template_in,
        template_name=CONFIRMATION_SUBSCRIPTION_TEMPLATE_NAME,
    )
    return new_template


@router.patch("/mailing/")
async def update_mailing_template(
    template_in: EmailTemplateUpdate,
    user: User = Depends(get_current_active_user),
):
    new_template = await email_template_service.update_template_content(
        template_in,
        template_name=MAILING_TEMPLATE_NAME,
    )
    return new_template
