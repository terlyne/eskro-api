import uuid

from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Project


async def get_projects(
    session: AsyncSession,
    is_active: bool = True,
    skip: int | None = None,
    limit: int | None = None,
) -> list[Project]:
    if is_active:
        if skip:
            stmt = (
                select(Project)
                .where(Project.is_active == True)
                .offset(skip)
                .order_by(desc(Project.created_at))
            )
            if limit:
                stmt = (
                    select(Project)
                    .where(Project.is_active == True)
                    .offset(skip)
                    .limit(limit)
                    .order_by(desc(Project.created_at))
                )
        else:
            stmt = (
                select(Project)
                .where(Project.is_active == True)
                .order_by(desc(Project.created_at))
            )
    else:
        if skip:
            stmt = select(Project).offset(skip).order_by(desc(Project.created_at))
            if limit:
                stmt = (
                    select(Project)
                    .offset(skip)
                    .limit(limit)
                    .order_by(desc(Project.created_at))
                )
        else:
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
) -> Project:
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
