import uuid

from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Project
from api.projects.schemas import ProjectCreate, ProjectUpdate


async def get_projects(
    session: AsyncSession,
) -> list[Project]:
    stmt = select(Project).order_by(desc(Project.created_at))
    result = await session.scalars(stmt)
    projects = result.all()

    return list(projects)


async def get_project_by_id(
    session: AsyncSession,
    project_id: uuid.UUID,
) -> Project | None:
    stmt = select(Project).where(Project.id == project_id)
    project = await session.scalar(stmt)

    return project


async def create_project(session: AsyncSession, **kw) -> Project:
    project = Project()
    for field, value in kw.items():
        if hasattr(project, field) and value:
            setattr(project, field, value)

    session.add(project)
    await session.commit()

    return project


async def update_project(
    session: AsyncSession,
    current_project: Project,
    **kw,
):
    for field, value in kw.items():
        if hasattr(current_project, field) and value:
            setattr(current_project, value)

    await session.commit()

    return current_project


async def delete_project(
    session: AsyncSession,
    project_id: uuid.UUID,
) -> bool:
    project = await get_project_by_id(session=session, project_id=project_id)
    if not project:
        return False

    await session.delete(project)
    await session.commit()

    return True
