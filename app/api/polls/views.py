import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from core.models import User
from core.db_helper import db_helper
from api.dependencies import get_current_active_user
from api.polls import crud
from api.polls.schemas import (
    PollResponse,
    PollCreate,
    PollUpdate,
    QuestionCreate,
    AnswerCreate,
    AnswerResponse,
)


router = APIRouter()


@router.get("/", response_model=list[PollResponse])
async def get_polls_with_questions_and_answers(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    polls = await crud.get_polls_with_questions_and_answers(session=session)
    return polls


@router.post("/", response_model=PollResponse)
async def create_poll(
    poll_in: PollCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    poll = await crud.create_poll(session=session, poll_in=poll_in)
    return poll


@router.patch("/{poll_id}/", response_model=PollResponse)
async def update_poll(
    poll_id: uuid.UUID,
    poll_in: PollUpdate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_poll = await crud.get_poll_by_id(session=session, poll_id=poll_id)
    if not current_poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    poll = await crud.update_poll(
        session=session,
        current_poll=current_poll,
        poll_in=poll_in,
    )
    return poll


@router.delete("/{poll_id}/")
async def delete_poll(
    poll_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_poll = await crud.get_poll_by_id(session=session, poll_id=poll_id)
    if not current_poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    await crud.delete_poll(session=session, current_poll=current_poll)

    return {"message": "success"}


@router.post("/{poll_id}/questions/", response_model=PollResponse)
async def create_question(
    poll_id: uuid.UUID,
    question_in: QuestionCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_poll = await crud.get_poll_by_id(session=session, poll_id=poll_id)
    if not current_poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    poll = await crud.create_question(
        session=session,
        current_poll=current_poll,
        question_in=question_in,
    )

    return poll


@router.delete("/{poll_id}/questions/{question_id}/")
async def delete_question(
    poll_id: uuid.UUID,
    question_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_poll = await crud.get_poll_by_id(session=session, poll_id=poll_id)
    if not current_poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    current_question = await crud.get_question_by_id(
        session=session, question_id=question_id
    )
    if not current_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    if current_question.poll_id != current_poll.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this poll",
        )

    await crud.delete_question(session=session, current_question=current_question)
    return {"message": "success"}


@router.post(
    "/{poll_id}/questions/{question_id}/answers/",
    response_model=AnswerResponse,
)
async def answer_to_question(
    poll_id: uuid.UUID,
    question_id: uuid.UUID,
    answer_in: AnswerCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_poll = await crud.get_poll_by_id(session=session, poll_id=poll_id)
    if not current_poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    current_question = await crud.get_question_by_id(
        session=session, question_id=question_id
    )
    if not current_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    if current_question.poll_id != current_poll.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this poll",
        )

    answer = await crud.create_answer(
        session=session,
        current_question=current_question,
        answer_in=answer_in,
    )

    return answer
