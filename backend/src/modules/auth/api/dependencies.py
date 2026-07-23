from typing import Annotated

from fastapi import Depends

from src.core.redis import RedisService, get_redis_service
from src.modules.user.api.dependencies import (
    PasswordHasher,
    get_password_hasher,
    get_user_repository,
)
from src.modules.user.application.repository import IUserRepository

from ..application.auth_service import AuthService
from ..application.notifier import IMailNotifier
from ..application.security import ITokenService
from ..application.store import IAuthStore
from ..infrastructure.auth_store import RedisAuthStore
from ..infrastructure.jwt_token_service import JWTTokenService
from ..infrastructure.mail_notifier import TaskiqMailNotifier


def get_token_service(
    redis: Annotated[RedisService, Depends(get_redis_service)],
) -> ITokenService:
    return JWTTokenService(redis)


def get_auth_store(
    redis: Annotated[RedisService, Depends(get_redis_service)],
) -> IAuthStore:
    return RedisAuthStore(redis)


def get_mail_notifier() -> IMailNotifier:
    return TaskiqMailNotifier()


def get_auth_service(
    users: Annotated[IUserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    tokens: Annotated[ITokenService, Depends(get_token_service)],
    store: Annotated[IAuthStore, Depends(get_auth_store)],
    notifier: Annotated[IMailNotifier, Depends(get_mail_notifier)],
) -> AuthService:
    return AuthService(users, hasher, tokens, store, notifier)
