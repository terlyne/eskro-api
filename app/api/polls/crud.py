import uuid

from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Poll, PollQuestion, PollAnswer
from api.polls.schemas import PollCreate, PollUpdate, QuestionCreate, AnswerCreate


async def get_polls_with_questions_and_answers(
    session: AsyncSession,
) -> list[Poll]:
    stmt = (
        select(Poll)
        .options(selectinload(Poll.questions).selectinload(PollQuestion.answers))
        .order_by(desc(Poll.created_at))
    )

    result = await session.scalars(stmt)
    return list(result.unique().all())


async def get_poll_by_id(
    session: AsyncSession,
    poll_id: uuid.UUID,
) -> Poll | None:
    stmt = (
        select(Poll)
        .options(selectinload(Poll.questions).selectinload(PollQuestion.answers))
        .where(Poll.id == poll_id)
    )

    poll = await session.scalar(stmt)

    return poll


async def update_poll(
    session: AsyncSession,
    current_poll: Poll,
    poll_in: PollUpdate,
) -> Poll:
    update_data = poll_in.model_dump(exclude_none=True)

    for field, value in update_data.items():
        setattr(current_poll, field, value)

    await session.commit()

    return current_poll


async def create_poll(
    session: AsyncSession,
    poll_in: PollCreate,
) -> Poll:
    poll = Poll(**poll_in.model_dump())
    session.add(poll)

    await session.commit()
    stmt = (
        select(Poll)
        .where(Poll.id == poll.id)
        .options(selectinload(Poll.questions).selectinload(PollQuestion.answers))
    )
    poll_with_relations = await session.scalar(stmt)

    return poll_with_relations


async def get_question_by_id(
    session: AsyncSession,
    question_id: uuid.UUID,
) -> PollQuestion | None:
    stmt = (
        select(PollQuestion)
        .options(selectinload(PollQuestion.answers))
        .where(PollQuestion.id == question_id)
    )
    question = await session.scalar(stmt)

    return question


async def create_question(
    session: AsyncSession,
    current_poll: Poll,
    question_in: QuestionCreate,
) -> Poll:
    question = PollQuestion(**question_in.model_dump())
    current_poll.questions.append(question)

    await session.commit()

    stmt = (
        select(Poll)
        .where(Poll.id == current_poll.id)
        .options(selectinload(Poll.questions).selectinload(PollQuestion.answers))
    )
    poll = await session.scalar(stmt)

    return poll


async def delete_question(
    session: AsyncSession,
    current_question: PollQuestion,
):
    await session.delete(current_question)
    await session.commit()


async def create_answer(
    session: AsyncSession,
    current_question: PollQuestion,
    answer_in: AnswerCreate,
) -> PollAnswer:
    answer = PollAnswer(**answer_in.model_dump())
    current_question.answers.append(answer)

    await session.commit()
    await session.refresh(answer)

    return answer


async def delete_poll(
    session: AsyncSession,
    current_poll: Poll,
):
    await session.delete(current_poll)
    await session.commit()
