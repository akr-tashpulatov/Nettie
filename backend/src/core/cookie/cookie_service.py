from typing import Literal

from fastapi import Request, Response

from src.core.config import settings


class CookieService:
    def set_cookie(
        self,
        response: Response,
        cookie_key: str,
        value: str,
        expires_in: int,
        *,
        http_only: bool = True,
        same_site: Literal["lax", "strict", "none"] = "lax",
        path: str = "/",
    ) -> None:
        response.set_cookie(
            cookie_key,
            value,
            path=path,
            max_age=expires_in,
            httponly=http_only,
            samesite=same_site,
            secure=settings.ENVIRONMENT not in ("local", "testing"),
        )

    def get_cookie(self, request: Request, cookie_key: str) -> str | None:
        return request.cookies.get(cookie_key)

    def delete_cookie(
        self, response: Response, cookie_key: str, path: str = "/"
    ) -> None:
        response.delete_cookie(cookie_key, path=path)
