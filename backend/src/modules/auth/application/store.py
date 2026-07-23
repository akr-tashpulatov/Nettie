from dataclasses import dataclass
from typing import Literal, Protocol

SendScope = Literal["signup", "reset"]


@dataclass
class SignUpSession:
    """Bookkeeping for an in-progress sign-up verification."""

    user_id: int
    email: str
    attempts: int
    send_count: int
    last_sent_at: float


@dataclass
class ResetSession:
    """Bookkeeping for password-reset link resends, keyed by email."""

    token: str
    send_count: int
    last_sent_at: float


@dataclass
class ResetToken:
    user_id: int
    email: str


class IAuthStore(Protocol):
    """Port over the transient auth state kept in Redis: sign-up sessions, OTP
    hashes, password-reset tokens and the per-email daily send counters.
    """

    # --- sign-up session + OTP ---------------------------------------------
    async def save_signup_session(
        self, session_id: str, session: SignUpSession
    ) -> None: ...

    async def get_signup_session(self, session_id: str) -> SignUpSession | None: ...

    async def save_otp(self, session_id: str, otp_hash: str) -> None: ...

    async def get_otp(self, session_id: str) -> str | None: ...

    async def delete_otp(self, session_id: str) -> None: ...

    async def clear_signup(self, session_id: str) -> None: ...

    # --- password-reset token + session ------------------------------------
    async def save_reset_token(self, token: str, record: ResetToken) -> None: ...

    async def get_reset_token(self, token: str) -> ResetToken | None: ...

    async def delete_reset_token(self, token: str) -> None: ...

    async def save_reset_session(self, email: str, session: ResetSession) -> None: ...

    async def get_reset_session(self, email: str) -> ResetSession | None: ...

    # --- per-email daily send counter --------------------------------------
    async def daily_count(self, scope: SendScope, email: str) -> int: ...

    async def incr_daily(self, scope: SendScope, email: str) -> int: ...
