import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.db_helper import db_helper
from api.dependencies import get_current_active_user
from api.projects.schemas import ProjectResponse, ProjectCreate, ProjectUpdate
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
    project_in: ProjectCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    project = await crud.create_project(session=session, project_in=project_in)
    return project


@router.patch("/{project_id}/", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    project = await crud.update_project(
        session=session, project_id=project_id, project_in=project_in
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
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
