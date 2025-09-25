import uuid

from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Feedback
from api.feedbacks.schemas import FeedbackCreate, FeedbackAnswer


async def get_feedbacks(
    session: AsyncSession,
    is_active: bool = True,
) -> list[Feedback]:
    if is_active:
        stmt = (
            select(Feedback).where(is_active=True).order_by(desc(Feedback.created_at))
        )
    else:
        stmt = select(Feedback).order_by(desc(Feedback.created_at))

    result = await session.scalars(stmt)
    feedbacks = result.all()

    return feedbacks


async def get_feedback_by_id(
    session: AsyncSession, feedback_id: uuid.UUID
) -> Feedback | None:
    stmt = select(Feedback).where(Feedback.id == feedback_id)
    feedback = await session.scalar(stmt)

    return feedback


async def create_feedback(
    session: AsyncSession,
    feedback_in: FeedbackCreate,
) -> Feedback:
    feedback = Feedback(**feedback_in.model_dump())
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)

    return feedback


async def delete_feedback(
    session: AsyncSession,
    feedback_id: uuid.UUID,
) -> bool:
    feedback = await get_feedback_by_id(session=session, feedback_id=feedback_id)
    if not feedback:
        return False

    await session.delete(feedback)
    await session.commit()

    return True


async def answer_feedback(
    session: AsyncSession,
    feedback_id: uuid.UUID,
    feedback_answer: FeedbackAnswer,
) -> Feedback | None:
    feedback = await get_feedback_by_id(session=session, feedback_id=feedback_id)
    if not feedback:
        return None

    feedback.is_answered = True
    feedback.response = feedback_answer.response
    await session.commit()

    return feedback
