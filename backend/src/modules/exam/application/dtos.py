from dataclasses import dataclass

from src.core.dtos.pagination import PaginationParams


@dataclass(frozen=True)
class AnswerDto:
    question_id: int
    selected_option_id: int


class SessionsQueryDto(PaginationParams):
    pass
