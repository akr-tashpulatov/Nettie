from datetime import datetime

from pydantic import BaseModel, Field

from src.core.dtos.pagination import PaginatedResponse
from src.models.enums import TestMode

from ..domain.entities import Question, Test


class TestCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    mode: TestMode


class TestUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    mode: TestMode | None = None


class TestResponse(BaseModel):
    id: int
    name: str
    mode: TestMode
    question_count: int
    created_at: datetime

    @classmethod
    def from_entity(cls, test: Test) -> "TestResponse":
        return cls(
            id=test.require_id,
            name=test.name,
            mode=test.mode,
            question_count=test.question_count,
            created_at=test.require_created_at,
        )


class TestsList(PaginatedResponse[TestResponse]):
    @classmethod
    def from_domain(cls, page: PaginatedResponse[Test]) -> "TestsList":
        return cls(
            page=page.page,
            limit=page.limit,
            items=[TestResponse.from_entity(t) for t in page.items],
            page_count=page.page_count,
            total_count=page.total_count,
        )


class OptionInput(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool


class QuestionCreate(BaseModel):
    text: str = Field(min_length=1)
    options: list[OptionInput] = Field(min_length=2)


class QuestionUpdate(BaseModel):
    text: str = Field(min_length=1)
    options: list[OptionInput] = Field(min_length=2)


class OptionResponse(BaseModel):
    id: int
    text: str
    is_correct: bool
    position: int


class QuestionResponse(BaseModel):
    id: int
    text: str
    position: int
    options: list[OptionResponse]

    @classmethod
    def from_entity(cls, question: Question) -> "QuestionResponse":
        return cls(
            id=question.require_id,
            text=question.text,
            position=question.position,
            options=[
                OptionResponse(
                    id=o.require_id,
                    text=o.text,
                    is_correct=o.is_correct,
                    position=o.position,
                )
                for o in question.options
            ],
        )


class ImportResult(BaseModel):
    imported_count: int


class StudentTestResponse(BaseModel):
    id: int
    name: str
    mode: TestMode
    question_count: int

    @classmethod
    def from_entity(cls, test: Test) -> "StudentTestResponse":
        return cls(
            id=test.require_id,
            name=test.name,
            mode=test.mode,
            question_count=test.question_count,
        )


class StudentTestsList(PaginatedResponse[StudentTestResponse]):
    @classmethod
    def from_domain(cls, page: PaginatedResponse[Test]) -> "StudentTestsList":
        return cls(
            page=page.page,
            limit=page.limit,
            items=[StudentTestResponse.from_entity(t) for t in page.items],
            page_count=page.page_count,
            total_count=page.total_count,
        )
