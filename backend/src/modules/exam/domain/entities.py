from dataclasses import dataclass, field
from datetime import datetime

from src.core.domain import Entity, TimestampedEntity
from src.models.enums import SessionStatus

from .exceptions import (
    InvalidOptionError,
    QuestionAlreadyAnsweredError,
    QuestionNotInSessionError,
    SessionCompletedError,
)


@dataclass(frozen=True)
class AnswerFeedback:
    is_correct: bool
    correct_option_id: int
    selected_option_id: int
    answered_count: int
    total: int
    completed: bool


@dataclass(kw_only=True)
class SessionItem(Entity):
    question_id: int
    position: int
    selected_option_id: int | None = None
    is_correct: bool | None = None
    answered_at: datetime | None = None

    @property
    def is_answered(self) -> bool:
        return self.answered_at is not None

    def answer(
        self, *, selected_option_id: int, correct_option_id: int, now: datetime
    ) -> None:
        self.selected_option_id = selected_option_id
        self.is_correct = selected_option_id == correct_option_id
        self.answered_at = now


@dataclass(kw_only=True)
class TestSession(TimestampedEntity):
    test_id: int
    student_id: int
    status: SessionStatus = SessionStatus.IN_PROGRESS
    total: int = 0
    correct_count: int = 0
    completed_at: datetime | None = None
    items: list[SessionItem] = field(default_factory=list)

    @classmethod
    def start(
        cls, *, test_id: int, student_id: int, question_ids: list[int]
    ) -> "TestSession":
        items = [
            SessionItem(question_id=qid, position=index)
            for index, qid in enumerate(question_ids)
        ]
        return cls(
            test_id=test_id,
            student_id=student_id,
            total=len(items),
            items=items,
        )

    @property
    def answered_count(self) -> int:
        return sum(1 for item in self.items if item.is_answered)

    def answer(
        self,
        *,
        question_id: int,
        selected_option_id: int,
        correct_option_id: int,
        valid_option_ids: set[int],
        now: datetime,
    ) -> tuple[SessionItem, AnswerFeedback]:
        if self.status is SessionStatus.COMPLETED:
            raise SessionCompletedError()

        item = next((i for i in self.items if i.question_id == question_id), None)
        if item is None:
            raise QuestionNotInSessionError()
        if item.is_answered:
            raise QuestionAlreadyAnsweredError()
        if selected_option_id not in valid_option_ids:
            raise InvalidOptionError()

        item.answer(
            selected_option_id=selected_option_id,
            correct_option_id=correct_option_id,
            now=now,
        )
        if item.is_correct:
            self.correct_count += 1
        if self.answered_count == self.total:
            self.status = SessionStatus.COMPLETED
            self.completed_at = now

        feedback = AnswerFeedback(
            is_correct=bool(item.is_correct),
            correct_option_id=correct_option_id,
            selected_option_id=selected_option_id,
            answered_count=self.answered_count,
            total=self.total,
            completed=self.status is SessionStatus.COMPLETED,
        )
        return item, feedback
