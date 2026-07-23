from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AnswerKey:
    correct_option_id: int
    valid_option_ids: set[int]


@dataclass(frozen=True)
class OptionView:
    id: int
    text: str
    position: int


@dataclass(frozen=True)
class QuestionView:
    id: int
    text: str
    options: list[OptionView]


class IQuestionCatalog(Protocol):
    """Read-only port over the `test` module's data.

    Lets the exam module select questions, render them to the student (without
    revealing the correct answer), and grade answers — without importing the
    `test` module. Implemented in `exam/infrastructure` against the shared
    `src/models` tables.
    """

    async def get_mode(self, test_id: int) -> int | None: ...

    async def count_by_test(self, test_id: int) -> int: ...

    async def random_ids(self, test_id: int, n: int) -> list[int]: ...

    async def get_answer_key(self, question_id: int) -> AnswerKey | None: ...

    async def get_question_views(
        self, question_ids: list[int]
    ) -> dict[int, QuestionView]:
        """Question text and options (no `is_correct`) keyed by question id."""
        ...
