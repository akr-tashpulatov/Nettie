from typing import Any

from fastapi import status

from src.core.domain import DomainException

from .main import DOMAIN_STATUS


def _status_for(exc: type[DomainException]) -> int:
    return next(
        (code for base, code in DOMAIN_STATUS.items() if issubclass(exc, base)),
        status.HTTP_400_BAD_REQUEST,
    )


def error_responses(
    *exceptions: type[DomainException],
) -> dict[int | str, dict[str, Any]]:
    """Build an OpenAPI `responses` dict documenting the given domain exceptions.

    Exceptions are grouped by their mapped HTTP status code, each rendered as a
    named example under that status so multiple error causes for the same code
    (e.g. two 401s) all show up in the docs instead of overwriting each other.
    """
    grouped: dict[int, dict[str, dict[str, Any]]] = {}
    for exc in exceptions:
        detail = (exc.__doc__ or "").strip()
        grouped.setdefault(_status_for(exc), {})[exc.__name__] = {
            "summary": exc.__name__,
            "value": {"detail": detail},
        }
    return {
        code: {"content": {"application/json": {"examples": examples}}}
        for code, examples in grouped.items()
    }
