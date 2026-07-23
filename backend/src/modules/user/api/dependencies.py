from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.audit import IAuditLogger, get_audit_logger
from src.core.database import get_session
from src.core.redis import RedisService, get_redis_service
from src.modules.auth.infrastructure.jwt_token_service import JWTTokenService

from ..application.repository import IUserRepository
from ..application.security import PasswordHasher
from ..application.sessions import ISessionRevoker
from ..application.user_service import UserService
from ..infrastructure.password_hasher import Argon2PasswordHasher
from ..infrastructure.user_repository import UserRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IUserRepository:
    return UserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()


def get_session_revoker(
    redis: Annotated[RedisService, Depends(get_redis_service)],
) -> ISessionRevoker:
    return JWTTokenService(redis)


def get_user_service(
    repo: Annotated[IUserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    audit: Annotated[IAuditLogger, Depends(get_audit_logger)],
    sessions: Annotated[ISessionRevoker, Depends(get_session_revoker)],
) -> UserService:
    return UserService(repo, hasher, audit, sessions)
