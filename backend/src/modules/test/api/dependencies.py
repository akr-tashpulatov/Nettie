from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session

from ..application.parsing import IQuestionParser
from ..application.repository import IQuestionRepository, ITestRepository
from ..application.test_service import TestService
from ..infrastructure.docx_parser import DocxQuestionParser
from ..infrastructure.question_repository import QuestionRepository
from ..infrastructure.test_repository import TestRepository


def get_test_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ITestRepository:
    return TestRepository(session)


def get_question_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IQuestionRepository:
    return QuestionRepository(session)


def get_question_parser() -> IQuestionParser:
    return DocxQuestionParser()


def get_test_service(
    tests: Annotated[ITestRepository, Depends(get_test_repository)],
    questions: Annotated[IQuestionRepository, Depends(get_question_repository)],
    parser: Annotated[IQuestionParser, Depends(get_question_parser)],
) -> TestService:
    return TestService(tests, questions, parser)
