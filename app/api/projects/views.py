from typing import Annotated
import uuid

from fastapi import APIRouter, UploadFile, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from core.file.service import file_service, PROJECTS_IMAGES_FOLDER
from api.dependencies import get_current_active_user
from api.projects.schemas import ProjectResponse
from api.projects import crud


router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    projects = await crud.get_projects(session=session)

    return projects


@router.get("/{project_id}/", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    project = await crud.get_project_by_id(session=session, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.post("/", response_model=ProjectResponse)
async def create_project(
    title: Annotated[str, Form()],
    body: Annotated[str, Form()],
    keywords: Annotated[list[str], Form()],
    min_text: Annotated[str, Form()],
    image: UploadFile,
    theme: Annotated[str, Form(max_length=100)],
    category: Annotated[str, Form(max_length=100)],
    is_active: Annotated[bool, Form()] = True,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    image_url = await file_service.save_image_file(
        upload_file=image, subdirectory=PROJECTS_IMAGES_FOLDER
    )
    project = await crud.create_project(
        session=session,
        title=title,
        body=body,
        keywords=keywords,
        min_text=min_text,
        image_url=image_url,
        theme=theme,
        category=category,
        is_active=is_active,
    )

    return project


@router.patch("/{project_id}/", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    title: Annotated[str | None, Form()] = None,
    body: Annotated[str | None, Form()] = None,
    keywords: Annotated[list[str] | None, Form()] = None,
    min_text: Annotated[str | None, Form()] = None,
    image: UploadFile | None = None,
    theme: Annotated[str | None, Form(max_length=100)] = None,
    category: Annotated[str | None, Form(max_length=100)] = None,
    is_active: Annotated[bool | None, Form()] = None,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_project = await crud.get_project_by_id(
        session=session,
        project_id=project_id,
    )
    if not current_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if image:
        await file_service.delete_file(current_project.image_url)
        image_url = await file_service.save_file(
            image, subdirectory=PROJECTS_IMAGES_FOLDER
        )

    project = await crud.update_project(
        session=session,
        current_project=current_project,
        title=title,
        body=body,
        keywords=keywords,
        min_text=min_text,
        image_url=image_url,
        theme=theme,
        category=category,
        is_active=is_active,
    )

    return project


@router.delete("/{project_id}/")
async def delete_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_project(session=session, project_id=project_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return {"message": "success"}
