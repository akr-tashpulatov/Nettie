import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.core.config import settings
from src.core.redis import RedisService
from src.models.enums import Role
from src.modules.auth.application.dtos import (
    AccessTokenClaims,
    RefreshTokenClaims,
    TokenPair,
)
from src.modules.auth.domain.exceptions import (
    InvalidAccessTokenError,
    InvalidRefreshTokenError,
)
from src.modules.user.domain.entities import User


def _allowlist_key(user_id: int) -> str:
    return f"auth:refresh:{user_id}"


class JWTTokenService:
    """PyJWT implementation of ITokenService.

    Access tokens are stateless. Refresh tokens carry a ``jti`` that is tracked
    in a per-user Redis set (the allowlist), which enables rotation on refresh
    and bulk revocation (e.g. after a password reset).
    """

    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    async def issue_pair(self, user: User) -> TokenPair:
        if user.id is None:
            raise InvalidRefreshTokenError("User is not persisted.")
        return await self._issue(user.id, self._user_claims(user))

    def verify_access(self, token: str) -> AccessTokenClaims:
        try:
            claims = self._decode(token, settings.JWT_SECRET)
        except InvalidRefreshTokenError as exc:
            raise InvalidAccessTokenError() from exc
        if claims.get("type") != "access":
            raise InvalidAccessTokenError()
        try:
            return AccessTokenClaims(
                sub=int(claims["sub"]),
                role=Role(claims["role"]),
                email=claims.get("email", ""),
                full_name=claims.get("full_name", ""),
                phone_number=claims.get("phone_number"),
            )
        except (KeyError, ValueError) as exc:
            raise InvalidAccessTokenError() from exc

    def verify_refresh(self, token: str) -> RefreshTokenClaims:
        claims = self._decode(token, settings.JWT_REFRESH_SECRET)
        if claims.get("type") != "refresh":
            raise InvalidRefreshTokenError()
        try:
            return RefreshTokenClaims(sub=int(claims["sub"]), jti=claims["jti"])
        except (KeyError, ValueError) as exc:
            raise InvalidRefreshTokenError() from exc

    async def rotate(self, claims: RefreshTokenClaims, user: User) -> TokenPair:
        # Atomically consume the jti from the allowlist; raises if absent or
        # already used (srem returns the count of removed members, so 0 → reuse).
        if not await self.redis.srem(_allowlist_key(claims.sub), claims.jti):
            raise InvalidRefreshTokenError()

        return await self._issue(claims.sub, self._user_claims(user))

    async def revoke(self, refresh_token: str) -> None:
        # Best-effort single-session logout: drop this token's jti from the
        # allowlist. A malformed/expired token is simply a no-op.
        try:
            claims = self._decode(refresh_token, settings.JWT_REFRESH_SECRET)
        except InvalidRefreshTokenError:
            return
        user_id = int(claims["sub"])
        await self.redis.srem(_allowlist_key(user_id), claims.get("jti", ""))

    async def revoke_all(self, user_id: int) -> None:
        await self.redis.delete(_allowlist_key(user_id))

    # --- internals ---------------------------------------------------------
    @staticmethod
    def _user_claims(user: User) -> dict[str, Any]:
        return {
            "sub": str(user.id),
            "role": user.role.value,
            "email": user.email.value,
            "phone_number": user.phone_number.value,
            "full_name": user.full_name,
        }

    async def _issue(self, user_id: int, identity: dict[str, Any]) -> TokenPair:
        now = datetime.now(timezone.utc)
        access_expires = now + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_expires = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = jwt.encode(
            {
                **identity,
                "jti": uuid.uuid4().hex,
                "type": "access",
                "iat": now,
                "exp": access_expires,
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        refresh_jti = uuid.uuid4().hex
        refresh_token = jwt.encode(
            {
                **identity,
                "jti": refresh_jti,
                "type": "refresh",
                "iat": now,
                "exp": refresh_expires,
            },
            settings.JWT_REFRESH_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Track the refresh jti so it can be rotated/revoked.
        await self.redis.sadd(_allowlist_key(user_id), refresh_jti)
        await self.redis.expire(
            _allowlist_key(user_id),
            settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return TokenPair(
            expires_in=expires_in,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    def _decode(token: str, secret: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        except jwt.PyJWTError as exc:
            raise InvalidRefreshTokenError() from exc
