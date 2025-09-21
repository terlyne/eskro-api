import uuid

from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Document


async def create_document(
    session: AsyncSession,
    file_url: str,
    title: str,
    is_active: bool = True,
) -> Document:
    document = Document(
        file_url=file_url,
        title=title,
        is_active=is_active,
    )

    session.add(document)
    await session.commit()
    await session.refresh(document)

    return document


async def get_documents(session: AsyncSession) -> list[Document]:
    stmt = select(Document).order_by(desc(Document.created_at))
    result = await session.scalars(stmt)
    documents = result.all()
    return list(documents)


async def get_document_by_id(
    session: AsyncSession,
    document_id: uuid.UUID,
) -> Document | None:
    stmt = select(Document).where(Document.id == document_id)
    document = await session.scalar(stmt)

    return document


async def update_document(
    session: AsyncSession,
    current_document: Document,
    **kw,
) -> Document:
    for field, value in kw.items():
        if value and hasattr(current_document, field):
            setattr(current_document, field, value)

    await session.commit()

    return current_document


async def delete_document(session: AsyncSession, document_id: uuid.UUID) -> bool:
    document = await get_document_by_id(session=session, document_id=document_id)
    if not document:
        return False

    await session.delete(document)
    await session.commit()

    return True
