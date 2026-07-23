from typing import Protocol

from ..domain.entities import Question, Test
from .dtos import TestsQueryDto


class ITestRepository(Protocol):
    """Port the application depends on for tests. Implemented in infrastructure."""

    async def add(self, test: Test) -> Test: ...

    async def get_by_id(self, test_id: int) -> Test | None: ...

    async def get_many(self, query: TestsQueryDto) -> tuple[list[Test], int]:
        """Return a page of tests with `question_count` populated. When
        `query.eligible_only`, only tests with `question_count >= mode`."""
        ...

    async def exists_by_name(
        self, name: str, exclude_id: int | None = None
    ) -> bool: ...

    async def update(self, test: Test) -> Test: ...

    async def delete(self, test_id: int) -> None: ...


class IQuestionRepository(Protocol):
    """Port the application depends on for questions. Implemented in
    infrastructure."""

    async def add(self, question: Question) -> Question: ...

    async def add_many(self, questions: list[Question]) -> int: ...

    async def get_by_id(self, question_id: int) -> Question | None: ...

    async def get_by_test(self, test_id: int) -> list[Question]: ...

    async def count_by_test(self, test_id: int) -> int: ...

    async def update(self, question: Question) -> Question: ...

    async def delete(self, question_id: int) -> None: ...
