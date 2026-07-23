from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session

from ..application.catalog import IQuestionCatalog
from ..application.repository import ISessionRepository
from ..application.session_service import SessionService
from ..infrastructure.question_catalog import SqlQuestionCatalog
from ..infrastructure.session_repository import SessionRepository


def get_session_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ISessionRepository:
    return SessionRepository(session)


def get_question_catalog(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IQuestionCatalog:
    return SqlQuestionCatalog(session)


def get_session_service(
    sessions: Annotated[ISessionRepository, Depends(get_session_repository)],
    catalog: Annotated[IQuestionCatalog, Depends(get_question_catalog)],
) -> SessionService:
    return SessionService(sessions, catalog)
