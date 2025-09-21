from typing import Annotated
import uuid

from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from core.file.service import file_service, PARTNERS_IMAGES_FOLDER
from api.dependencies import get_current_active_user
from api.partners.schemas import PartnerResponse
from api.partners import crud

router = APIRouter()


@router.get("/", response_model=list[PartnerResponse])
async def get_partners(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    partners = await crud.get_partners(session=session)
    return partners


@router.get("/{partner_id}/", response_model=PartnerResponse)
async def get_partner_by_id(
    partner_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    partner = await crud.get_partner_by_id(session=session, partner_id=partner_id)

    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    return partner


@router.post("/", response_model=PartnerResponse)
async def create_partner(
    logo: UploadFile,
    partner_name: Annotated[str, Form()],
    count_order: Annotated[int, Form(ge=1)],
    partner_url: Annotated[str | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    logo_url = await file_service.save_file(
        upload_file=logo,
        subdirectory=PARTNERS_IMAGES_FOLDER,
    )
    partner = await crud.create_partner(
        session=session,
        logo_url=logo_url,
        partner_name=partner_name,
        count_order=count_order,
        partner_url=partner_url,
    )

    return partner


@router.patch("/{partner_id}/", response_model=PartnerResponse)
async def update_partner(
    partner_id: uuid.UUID,
    logo: UploadFile | None = None,
    partner_name: Annotated[str | None, Form()] = None,
    count_order: Annotated[int | None, Form(ge=1)] = None,
    partner_url: Annotated[str | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_partner = await crud.get_partner_by_id(
        session=session, partner_id=partner_id
    )
    if not current_partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    if logo:
        await file_service.delete_file(current_partner.logo_url)
        logo_url = await file_service.save_file(
            upload_file=logo,
            subdirectory=PARTNERS_IMAGES_FOLDER,
        )

    partner = await crud.update_partner(
        session=session,
        current_partner=current_partner,
        logo_url=logo_url,
        partner_name=partner_name,
        count_order=count_order,
        partner_url=partner_url,
    )

    return partner


@router.delete("/{partner_id}/")
async def delete_partner(
    partner_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_partner(session=session, partner_id=partner_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    return {"message": "success"}
