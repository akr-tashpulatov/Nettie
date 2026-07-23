import random
from datetime import datetime

from pydantic import BaseModel

from src.core.dtos.pagination import PaginatedResponse
from src.models.enums import SessionStatus

from ..application.session_service import SessionDetail
from ..domain.entities import AnswerFeedback, TestSession


class AnswerRequest(BaseModel):
    question_id: int
    selected_option_id: int


class AnswerFeedbackResponse(BaseModel):
    is_correct: bool
    correct_option_id: int
    selected_option_id: int
    answered_count: int
    total: int
    completed: bool

    @classmethod
    def from_feedback(cls, feedback: AnswerFeedback) -> "AnswerFeedbackResponse":
        return cls(
            is_correct=feedback.is_correct,
            correct_option_id=feedback.correct_option_id,
            selected_option_id=feedback.selected_option_id,
            answered_count=feedback.answered_count,
            total=feedback.total,
            completed=feedback.completed,
        )


class SessionOptionView(BaseModel):
    id: int
    text: str
    position: int


class SessionItemView(BaseModel):
    position: int
    question_id: int
    text: str
    options: list[SessionOptionView]
    answered: bool
    selected_option_id: int | None
    is_correct: bool | None


class SessionResponse(BaseModel):
    id: int
    test_id: int
    status: SessionStatus
    total: int
    answered_count: int
    correct_count: int
    completed_at: datetime | None
    created_at: datetime
    items: list[SessionItemView]

    @classmethod
    def from_detail(cls, detail: SessionDetail) -> "SessionResponse":
        session = detail.session
        items = []
        for item in session.items:
            view = detail.questions.get(item.question_id)
            options = []
            if view:
                # Shuffle so the correct option isn't always first, seeded per
                # (session, question) so the order stays stable across reloads.
                ordered = list(view.options)
                random.Random(f"{session.require_id}:{item.question_id}").shuffle(
                    ordered
                )
                options = [
                    SessionOptionView(id=o.id, text=o.text, position=o.position)
                    for o in ordered
                ]
            items.append(
                SessionItemView(
                    position=item.position,
                    question_id=item.question_id,
                    text=view.text if view else "",
                    options=options,
                    answered=item.is_answered,
                    selected_option_id=item.selected_option_id,
                    is_correct=item.is_correct,
                )
            )
        return cls(
            id=session.require_id,
            test_id=session.test_id,
            status=session.status,
            total=session.total,
            answered_count=session.answered_count,
            correct_count=session.correct_count,
            completed_at=session.completed_at,
            created_at=session.require_created_at,
            items=items,
        )


class SessionSummaryResponse(BaseModel):
    id: int
    test_id: int
    status: SessionStatus
    total: int
    answered_count: int
    correct_count: int
    completed_at: datetime | None
    created_at: datetime

    @classmethod
    def from_entity(cls, session: TestSession) -> "SessionSummaryResponse":
        return cls(
            id=session.require_id,
            test_id=session.test_id,
            status=session.status,
            total=session.total,
            answered_count=session.answered_count,
            correct_count=session.correct_count,
            completed_at=session.completed_at,
            created_at=session.require_created_at,
        )


class SessionsList(PaginatedResponse[SessionSummaryResponse]):
    @classmethod
    def from_domain(cls, page: PaginatedResponse[TestSession]) -> "SessionsList":
        return cls(
            page=page.page,
            limit=page.limit,
            items=[SessionSummaryResponse.from_entity(s) for s in page.items],
            page_count=page.page_count,
            total_count=page.total_count,
        )
