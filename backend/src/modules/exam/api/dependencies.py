from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.openai import get_openai_client
from src.core.redis import RedisService, get_redis_service

from ..application.catalog import IQuestionCatalog
from ..application.explainer import IExplanationGenerator
from ..application.explanation_cache import IExplanationCache
from ..application.explanation_service import ExplanationService
from ..application.repository import ISessionRepository
from ..application.session_service import SessionService
from ..infrastructure.explanation_cache import RedisExplanationCache
from ..infrastructure.openai_explainer import OpenAIExplainer
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


def get_explanation_cache(
    redis: Annotated[RedisService, Depends(get_redis_service)],
) -> IExplanationCache:
    return RedisExplanationCache(redis)


def get_explanation_generator(
    client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
) -> IExplanationGenerator:
    return OpenAIExplainer(client)


def get_explanation_service(
    catalog: Annotated[IQuestionCatalog, Depends(get_question_catalog)],
    cache: Annotated[IExplanationCache, Depends(get_explanation_cache)],
    generator: Annotated[IExplanationGenerator, Depends(get_explanation_generator)],
) -> ExplanationService:
    return ExplanationService(catalog, cache, generator)
