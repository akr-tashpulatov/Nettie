import math
from dataclasses import dataclass
from datetime import datetime, timezone

from src.core.dtos.pagination import PaginatedResponse

from ..domain.entities import AnswerFeedback, TestSession
from ..domain.exceptions import (
    QuestionNotInSessionError,
    SessionForbiddenError,
    SessionNotFoundError,
    TestNotEligibleError,
    TestNotFoundError,
)
from .catalog import IQuestionCatalog, QuestionView
from .dtos import AnswerDto, SessionsQueryDto
from .repository import ISessionRepository


@dataclass(frozen=True)
class SessionDetail:
    """A session together with the content of its questions (answers hidden)."""

    session: TestSession
    questions: dict[int, QuestionView]


class SessionService:
    def __init__(self, sessions: ISessionRepository, catalog: IQuestionCatalog):
        self.sessions = sessions
        self.catalog = catalog

    async def start(self, test_id: int, student_id: int) -> SessionDetail:
        mode = await self.catalog.get_mode(test_id)
        if mode is None:
            raise TestNotFoundError()
        if await self.catalog.count_by_test(test_id) < mode:
            raise TestNotEligibleError()

        question_ids = await self.catalog.random_ids(test_id, mode)
        session = TestSession.start(
            test_id=test_id, student_id=student_id, question_ids=question_ids
        )
        session = await self.sessions.add(session)
        return await self._detail(session)

    async def get(self, session_id: int, student_id: int) -> SessionDetail:
        session = await self._get_owned(session_id, student_id)
        return await self._detail(session)

    async def _get_owned(self, session_id: int, student_id: int) -> TestSession:
        session = await self.sessions.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundError()
        if session.student_id != student_id:
            raise SessionForbiddenError()
        return session

    async def _detail(self, session: TestSession) -> SessionDetail:
        views = await self.catalog.get_question_views(
            [item.question_id for item in session.items]
        )
        return SessionDetail(session=session, questions=views)

    async def list_my_sessions(
        self, student_id: int, query: SessionsQueryDto
    ) -> PaginatedResponse[TestSession]:
        sessions, total = await self.sessions.get_many_by_student(student_id, query)
        return PaginatedResponse[TestSession](
            page=query.page,
            limit=query.limit,
            items=sessions,
            total_count=total,
            page_count=math.ceil(total / query.limit) if query.limit else 0,
        )

    async def answer(
        self, session_id: int, student_id: int, data: AnswerDto
    ) -> AnswerFeedback:
        session = await self._get_owned(session_id, student_id)

        key = await self.catalog.get_answer_key(data.question_id)
        if key is None:
            raise QuestionNotInSessionError()

        item, feedback = session.answer(
            question_id=data.question_id,
            selected_option_id=data.selected_option_id,
            correct_option_id=key.correct_option_id,
            valid_option_ids=key.valid_option_ids,
            now=datetime.now(timezone.utc),
        )
        await self.sessions.save_answer(item, session)
        return feedback
