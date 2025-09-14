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


async def create_project(
    session: AsyncSession,
    project_in: ProjectCreate,
) -> Project:
    project = Project(**project_in.model_dump())
    session.add(project)

    await session.commit()
    await session.refresh(project)

    return project


async def update_project(
    session: AsyncSession,
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
) -> Project | None:
    project = await get_project_by_id(session=session, project_id=project_id)
    if not project:
        return None

    update_data = project_in.model_dump(exclude_none=True)

    for field, value in update_data.items():
        setattr(project, field, value)

    await session.commit()
    await session.refresh(project)

    return project


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
