from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.core.domain import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainException,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from src.core.logger import logging

# Map domain error categories to HTTP status codes in one place. New domain
# exceptions inherit one of these bases and get the right status for free.
# Order matters: more specific subclasses must come before their bases
# (ValidationError is a BadRequestError, so it must be matched first).
DOMAIN_STATUS: dict[type[DomainException], int] = {
    ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    ServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        status_code = next(
            (code for base, code in DOMAIN_STATUS.items() if isinstance(exc, base)),
            status.HTTP_400_BAD_REQUEST,
        )
        return JSONResponse(status_code=status_code, content={"detail": exc.detail})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logging.error(
            "Database error on %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
