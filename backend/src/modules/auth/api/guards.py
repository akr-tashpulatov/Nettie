from typing import Annotated

from fastapi import Depends, Request

from src.core.cookie.cookie_service import CookieService
from src.models.enums import Role

from ..application.dtos import AccessTokenClaims
from ..application.security import ITokenService
from ..domain.exceptions import InsufficientRoleError, InvalidAccessTokenError
from .cookies import ACCESS_TOKEN_COOKIE, get_cookie_service
from .dependencies import get_token_service

_BEARER_PREFIX = "Bearer "


class AuthGuard:
    """FastAPI dependency that authenticates a request and enforces roles.

    The access token is read from the ``Authorization: Bearer`` header, falling
    back to the HttpOnly ``access_token`` cookie. Construct with the roles the
    route allows; no roles means "any authenticated user".
    """

    def __init__(self, *roles: Role) -> None:
        self.roles = roles

    async def __call__(
        self,
        request: Request,
        tokens: Annotated[ITokenService, Depends(get_token_service)],
        cookies: Annotated[CookieService, Depends(get_cookie_service)],
    ) -> AccessTokenClaims:
        token = self._extract(request, cookies)
        if token is None:
            raise InvalidAccessTokenError()
        claims = tokens.verify_access(token)
        if self.roles and claims.role not in self.roles:
            raise InsufficientRoleError()
        return claims

    @staticmethod
    def _extract(request: Request, cookies: CookieService) -> str | None:
        header = request.headers.get("Authorization")
        if header and header.startswith(_BEARER_PREFIX):
            token = header[len(_BEARER_PREFIX) :].strip()
            if token:
                return token
        return cookies.get_cookie(request, ACCESS_TOKEN_COOKIE)


require_any = AuthGuard()
require_admin = AuthGuard(Role.ADMIN)
require_student = AuthGuard(Role.STUDENT)

AuthUser = Annotated[AccessTokenClaims, Depends(require_any)]
AdminUser = Annotated[AccessTokenClaims, Depends(require_admin)]
StudentUser = Annotated[AccessTokenClaims, Depends(require_student)]
