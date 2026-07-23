from typing import Callable, cast

from fastapi import FastAPI, Request, Response
from slowapi import Limiter
from slowapi import _rate_limit_exceeded_handler as rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware as RateLimitMiddleware
from slowapi.util import get_remote_address

from src.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=settings.DEFAULT_RATE_LIMIT,
    headers_enabled=settings.RATE_LIMIT_HEADERS_ENABLED,
    storage_uri=settings.REDIS_URL(settings.RATE_LIMIT_DATABASE),
)


def setup(app: FastAPI) -> None:
    app.state.limiter = limiter
    app.add_middleware(RateLimitMiddleware)
    app.add_exception_handler(
        RateLimitExceeded,
        cast("Callable[[Request, Exception], Response]", rate_limit_exceeded_handler),
    )
