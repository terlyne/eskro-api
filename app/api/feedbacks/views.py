import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from core.models import User
from core.email.service import email_service
from api.dependencies import get_current_active_user
from api.feedbacks.schemas import FeedbackResponse, FeedbackCreate, FeedbackAnswer
from api.feedbacks import crud

router = APIRouter()


@router.get("/", response_model=list[FeedbackResponse])
async def get_feedbacks(
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    feedbacks = await crud.get_feedbacks(session=session)
    return feedbacks


@router.get("/{feedback_id}/", response_model=FeedbackResponse)
async def get_feedback_by_id(
    feedback_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    feedback = await crud.get_feedback_by_id(session=session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    return feedback


@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_in: FeedbackCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Фидбек создают обычные пользователи
    feedback = await crud.create_feeadback(session=session, feedback_in=feedback_in)
    return feedback


@router.delete("/{feedback_id}/")
async def delete_feedback(
    feedback_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    is_deleted = await crud.delete_feedback(session=session, feedback_id=feedback_id)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    return {"message": "success"}


@router.post("/{feedback_id}/answer/", response_model=FeedbackResponse)
async def answer_feedback(
    feedback_answer: FeedbackAnswer,
    feedback_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """Эндпоинт для ответа с админ-панели на feedback"""
    feedback = await crud.answer_feedback(
        session=session, feedback_id=feedback_id, feedback_answer=feedback_answer
    )
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    # Отправляем ответ пользователю на почту
    if feedback.email:
        await email_service.send_response_to_feedback(
            email=feedback.email,
            first_name=feedback.first_name,
            middle_name=feedback.middle_name,
            question=feedback.message,
            response=feedback.response,
        )

    return feedback
