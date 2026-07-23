from fastapi import Response

from src.core.config import settings
from src.core.cookie.cookie_service import CookieService

from ..application.dtos import TokenPair

ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


def get_cookie_service() -> CookieService:
    return CookieService()


def set_auth_cookies(
    cookies: CookieService, response: Response, tokens: TokenPair
) -> None:
    """Persist the access and refresh tokens as HttpOnly cookies."""
    cookies.set_cookie(
        response,
        ACCESS_TOKEN_COOKIE,
        tokens.access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    cookies.set_cookie(
        response,
        REFRESH_TOKEN_COOKIE,
        tokens.refresh_token,
        expires_in=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def clear_auth_cookies(cookies: CookieService, response: Response) -> None:
    cookies.delete_cookie(response, ACCESS_TOKEN_COOKIE)
    cookies.delete_cookie(response, REFRESH_TOKEN_COOKIE)
