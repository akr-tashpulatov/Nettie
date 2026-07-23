from dataclasses import dataclass, field

from src.core.dtos.pagination import PaginationParams
from src.models.enums import TestMode


@dataclass(frozen=True)
class TestCreateDto:
    name: str
    mode: TestMode
    created_by: int


@dataclass(frozen=True)
class TestUpdateDto:
    name: str | None = None
    mode: TestMode | None = None


class TestsQueryDto(PaginationParams):
    query: str | None = None
    eligible_only: bool = False


@dataclass(frozen=True)
class OptionDto:
    text: str
    is_correct: bool


@dataclass(frozen=True)
class QuestionCreateDto:
    text: str
    options: list[OptionDto]


@dataclass(frozen=True)
class QuestionUpdateDto:
    text: str
    options: list[OptionDto]


@dataclass(frozen=True)
class ParsedQuestionDto:
    text: str
    options: list[OptionDto] = field(default_factory=list)
