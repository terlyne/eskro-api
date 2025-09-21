import uuid
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException, status

from core.models import User
from core.file.service import file_service, DOCUMENTS_FOLDER
from core.db_helper import db_helper
from api.dependencies import get_current_active_user
from api.documents import crud
from api.documents.schemas import DocumentResponse


router = APIRouter()


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    title: Annotated[str, Form()],
    is_active: Annotated[bool, Form()] = True,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    file_url = await file_service.save_file(file, DOCUMENTS_FOLDER)

    document = await crud.create_document(
        session=session,
        file_url=file_url,
        title=title,
        is_active=is_active,
    )
    return document


@router.get("/", response_model=list[DocumentResponse])
async def get_documents(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    documents = await crud.get_documents(session=session)
    return documents


@router.get("/{document_id}/", response_model=DocumentResponse)
async def get_document_by_id(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    document = await crud.get_document_by_id(session=session, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.patch("/{document_id}/", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    file: UploadFile | None = None,
    title: Annotated[str | None, Form()] = None,
    is_active: Annotated[bool | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_document = await crud.get_document_by_id(
        session=session, document_id=document_id
    )
    if not current_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if file:
        await file_service.delete_file(current_document.file_url)
        file_url = await file_service.save_file(file, DOCUMENTS_FOLDER)

    document = await crud.update_document(
        session=session,
        document=document,
        file_url=file_url,
        title=title,
        is_active=is_active,
    )

    return document


@router.delete("/{document_id}/deactivate/")
async def deactivate_document(
    document_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deactivated = await crud.deactivate_document(
        session=session, document_id=document_id
    )
    if not is_deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return {"message": "success"}


@router.delete("/{document_id}/")
async def delete_document(
    document_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_document(session=session, document_id=document_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return {"message": "success"}
