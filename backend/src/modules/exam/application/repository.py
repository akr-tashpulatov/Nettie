from typing import Protocol

from ..domain.entities import SessionItem, TestSession
from .dtos import SessionsQueryDto


class ISessionRepository(Protocol):
    """Port the application depends on. Implemented in the infrastructure layer."""

    async def add(self, session: TestSession) -> TestSession: ...

    async def get_by_id(self, session_id: int) -> TestSession | None: ...

    async def get_many_by_student(
        self, student_id: int, query: SessionsQueryDto
    ) -> tuple[list[TestSession], int]: ...

    async def save_answer(self, item: SessionItem, session: TestSession) -> None:
        """Persist a single answered item plus the session's updated
        `correct_count` / `status` / `completed_at`."""
        ...
