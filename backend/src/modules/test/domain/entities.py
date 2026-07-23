from dataclasses import dataclass, field

from src.core.domain import Entity, TimestampedEntity
from src.models.enums import TestMode

from .exceptions import InvalidQuestionError


@dataclass(kw_only=True)
class Option(Entity):
    text: str
    is_correct: bool
    position: int


@dataclass(kw_only=True)
class Question(Entity):
    test_id: int
    text: str
    position: int
    options: list[Option] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        test_id: int,
        text: str,
        position: int,
        options: list[tuple[str, bool]],
    ) -> "Question":
        question = cls(test_id=test_id, text=text.strip(), position=position)
        question.set_options(options)
        return question

    def set_options(self, options: list[tuple[str, bool]]) -> None:
        if len(options) < 2:
            raise InvalidQuestionError("A question needs at least two options.")
        if sum(1 for _, is_correct in options if is_correct) != 1:
            raise InvalidQuestionError("A question needs exactly one correct option.")
        self.options = [
            Option(text=text.strip(), is_correct=is_correct, position=index)
            for index, (text, is_correct) in enumerate(options)
        ]

    def edit(self, *, text: str, options: list[tuple[str, bool]]) -> None:
        self.text = text.strip()
        self.set_options(options)


@dataclass(kw_only=True)
class Test(TimestampedEntity):
    name: str
    mode: TestMode
    created_by: int
    question_count: int = 0

    @classmethod
    def create(cls, *, name: str, mode: TestMode, created_by: int) -> "Test":
        return cls(name=name.strip(), mode=mode, created_by=created_by)

    def rename(self, name: str) -> None:
        self.name = name.strip()

    def change_mode(self, mode: TestMode) -> None:
        self.mode = mode
