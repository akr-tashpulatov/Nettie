import json

from src.core.redis import RedisService
from src.modules.auth.application.store import (
    ResetSession,
    ResetToken,
    SendScope,
    SignUpSession,
)
from src.modules.auth.domain.constants import (
    DAILY_COUNTER_TTL_SECONDS,
    OTP_TTL_SECONDS,
    RESET_TOKEN_TTL_SECONDS,
    SIGNUP_SESSION_TTL_SECONDS,
)


def _signup_key(session_id: str) -> str:
    return f"auth:signup:{session_id}"


def _otp_key(session_id: str) -> str:
    return f"auth:signup:otp:{session_id}"


def _reset_token_key(token: str) -> str:
    return f"auth:reset:{token}"


def _reset_session_key(email: str) -> str:
    return f"auth:reset:email:{email}"


def _daily_key(scope: SendScope, email: str) -> str:
    return f"auth:daily:{scope}:{email}"


class RedisAuthStore:
    """Redis-backed implementation of IAuthStore.

    All structured records are stored as JSON strings (``RedisService.get``
    already json-decodes on read).
    """

    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    # --- sign-up session + OTP ---------------------------------------------
    async def save_signup_session(
        self, session_id: str, session: SignUpSession
    ) -> None:
        await self.redis.set(
            _signup_key(session_id),
            json.dumps(session.__dict__),
            ttl=SIGNUP_SESSION_TTL_SECONDS,
        )

    async def get_signup_session(self, session_id: str) -> SignUpSession | None:
        data = await self.redis.get(_signup_key(session_id))
        if not isinstance(data, dict):
            return None
        return SignUpSession(**data)

    async def save_otp(self, session_id: str, otp_hash: str) -> None:
        await self.redis.set(_otp_key(session_id), otp_hash, ttl=OTP_TTL_SECONDS)

    async def get_otp(self, session_id: str) -> str | None:
        data = await self.redis.get(_otp_key(session_id))
        return data if isinstance(data, str) else None

    async def delete_otp(self, session_id: str) -> None:
        await self.redis.delete(_otp_key(session_id))

    async def clear_signup(self, session_id: str) -> None:
        await self.redis.delete(_signup_key(session_id))
        await self.redis.delete(_otp_key(session_id))

    # --- password-reset token + session ------------------------------------
    async def save_reset_token(self, token: str, record: ResetToken) -> None:
        await self.redis.set(
            _reset_token_key(token),
            json.dumps(record.__dict__),
            ttl=RESET_TOKEN_TTL_SECONDS,
        )

    async def get_reset_token(self, token: str) -> ResetToken | None:
        data = await self.redis.get(_reset_token_key(token))
        if not isinstance(data, dict):
            return None
        return ResetToken(**data)

    async def delete_reset_token(self, token: str) -> None:
        await self.redis.delete(_reset_token_key(token))

    async def save_reset_session(self, email: str, session: ResetSession) -> None:
        await self.redis.set(
            _reset_session_key(email),
            json.dumps(session.__dict__),
            ttl=SIGNUP_SESSION_TTL_SECONDS,
        )

    async def get_reset_session(self, email: str) -> ResetSession | None:
        data = await self.redis.get(_reset_session_key(email))
        if not isinstance(data, dict):
            return None
        return ResetSession(**data)

    # --- per-email daily send counter --------------------------------------
    async def daily_count(self, scope: SendScope, email: str) -> int:
        data = await self.redis.get(_daily_key(scope, email))
        try:
            return int(data) if data is not None else 0
        except TypeError, ValueError:
            return 0

    async def incr_daily(self, scope: SendScope, email: str) -> int:
        key = _daily_key(scope, email)
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, DAILY_COUNTER_TTL_SECONDS)
        return count
