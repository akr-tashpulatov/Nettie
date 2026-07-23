from typing import Protocol

from src.modules.user.domain.entities import User

from .dtos import AccessTokenClaims, RefreshTokenClaims, TokenPair


class ITokenService(Protocol):
    """Port for issuing, verifying and rotating JWT access/refresh token pairs.

    Implemented in the infrastructure layer (PyJWT + a Redis allowlist for
    refresh-token rotation/revocation).
    """

    async def issue_pair(self, user: User) -> TokenPair: ...

    def verify_access(self, token: str) -> AccessTokenClaims: ...

    def verify_refresh(self, token: str) -> RefreshTokenClaims: ...

    async def rotate(self, claims: RefreshTokenClaims, user: User) -> TokenPair: ...

    async def revoke(self, refresh_token: str) -> None: ...

    async def revoke_all(self, user_id: int) -> None: ...
