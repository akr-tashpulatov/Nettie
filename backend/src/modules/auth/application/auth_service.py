import math
import secrets
import time

from src.core.config import settings
from src.models.enums import Role
from src.modules.user.application.repository import IUserRepository
from src.modules.user.application.security import PasswordHasher
from src.modules.user.domain.entities import User
from src.modules.user.domain.exceptions import (
    EmailAlreadyExistsError,
    PhoneNumberAlreadyExistsError,
)

from ..domain.constants import (
    DAILY_SEND_LIMIT,
    MAX_OTP_ATTEMPTS,
    cooldown_for,
)
from ..domain.exceptions import (
    DailySendLimitExceededError,
    EmailNotVerifiedError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InvalidResetVerificationTokenError,
    SignUpSessionExpiredError,
)
from .dtos import (
    ChangeSignUpEmailDto,
    ConfirmResetDto,
    RequestResetDto,
    SignInDto,
    SignUpDto,
    SignUpResult,
    TokenPair,
    VerifyOtpDto,
    VerifyResult,
)
from .notifier import IMailNotifier
from .security import ITokenService
from .store import IAuthStore, ResetSession, ResetToken, SignUpSession


class AuthService:
    def __init__(
        self,
        users: IUserRepository,
        hasher: PasswordHasher,
        tokens: ITokenService,
        store: IAuthStore,
        notifier: IMailNotifier,
    ) -> None:
        self.users = users
        self.hasher = hasher
        self.tokens = tokens
        self.store = store
        self.notifier = notifier

    # --- sign-up -----------------------------------------------------------
    async def sign_up(self, data: SignUpDto) -> SignUpResult:
        if await self.users.exists_by_email(data.email):
            raise EmailAlreadyExistsError()
        if await self.users.exists_by_phone_number(data.phone_number):
            raise PhoneNumberAlreadyExistsError()

        user = User.register(
            full_name=data.full_name,
            role=Role.STUDENT,
            email=data.email,
            phone_number=data.phone_number,
            password_hash=self.hasher.hash(data.password),
        )
        user.deactivate()  # unverified users stay inactive until they verify
        user = await self.users.add(user)

        email = user.email.value
        code = self._generate_otp()
        session_id = secrets.token_urlsafe(32)

        await self.store.save_otp(session_id, self.hasher.hash(str(code)))
        await self.store.save_signup_session(
            session_id,
            SignUpSession(
                user_id=user.require_id,
                email=email,
                attempts=0,
                send_count=1,
                last_sent_at=time.time(),
            ),
        )
        await self.store.incr_daily("signup", email)
        await self.notifier.send_verification_code(email, code)
        return SignUpResult(session_id=session_id, retry_after=cooldown_for(1))

    async def resend_code(self, session_id: str) -> SignUpResult:
        session = await self.store.get_signup_session(session_id)
        if session is None:
            raise SignUpSessionExpiredError()

        if await self.store.daily_count("signup", session.email) >= DAILY_SEND_LIMIT:
            raise DailySendLimitExceededError()

        remaining = self._cooldown_remaining(session.send_count, session.last_sent_at)
        if remaining > 0:
            # Still cooling down: tell the client how long to wait, don't resend.
            return SignUpResult(session_id=session_id, retry_after=remaining)

        code = self._generate_otp()
        await self.store.delete_otp(session_id)  # invalidate the previous code
        await self.store.save_otp(session_id, self.hasher.hash(str(code)))

        session.send_count += 1
        session.attempts = 0
        session.last_sent_at = time.time()
        await self.store.save_signup_session(session_id, session)
        await self.store.incr_daily("signup", session.email)
        await self.notifier.send_verification_code(session.email, code)
        return SignUpResult(
            session_id=session_id, retry_after=cooldown_for(session.send_count)
        )

    async def verify(self, data: VerifyOtpDto) -> VerifyResult:
        session = await self.store.get_signup_session(data.session_id)
        if session is None:
            raise SignUpSessionExpiredError()

        otp_hash = await self.store.get_otp(data.session_id)
        if otp_hash is None:
            # Code expired or already invalidated after too many attempts.
            return VerifyResult(success=False, code_invalidated=True)

        if not self.hasher.verify(str(data.otp_code), otp_hash):
            session.attempts += 1
            if session.attempts >= MAX_OTP_ATTEMPTS:
                await self.store.delete_otp(data.session_id)
                await self.store.save_signup_session(data.session_id, session)
                return VerifyResult(success=False, code_invalidated=True)
            await self.store.save_signup_session(data.session_id, session)
            return VerifyResult(success=False, code_invalidated=False)

        user = await self.users.get_by_id(session.user_id)
        if user is None:
            raise SignUpSessionExpiredError()
        user.verify_email()
        if not user.is_active:
            user.activate()
        user = await self.users.update(user)
        await self.store.clear_signup(data.session_id)

        tokens = await self.tokens.issue_pair(user)
        return VerifyResult(success=True, code_invalidated=False, tokens=tokens)

    async def change_signup_email(self, data: ChangeSignUpEmailDto) -> SignUpResult:
        session = await self.store.get_signup_session(data.session_id)
        if session is None:
            raise SignUpSessionExpiredError()

        # Throttle before any mutation: same guards as resend_code.
        if await self.store.daily_count("signup", data.email) >= DAILY_SEND_LIMIT:
            raise DailySendLimitExceededError()

        remaining = self._cooldown_remaining(session.send_count, session.last_sent_at)
        if remaining > 0:
            return SignUpResult(session_id=data.session_id, retry_after=remaining)

        user = await self.users.get_by_id(session.user_id)
        if user is None:
            raise SignUpSessionExpiredError()
        if await self.users.exists_by_email(data.email, exclude_id=user.id):
            raise EmailAlreadyExistsError()

        user.change_email(data.email)
        user = await self.users.update(user)
        email = user.email.value

        code = self._generate_otp()
        await self.store.delete_otp(data.session_id)
        await self.store.save_otp(data.session_id, self.hasher.hash(str(code)))
        session.email = email
        session.attempts = 0
        session.send_count = 1
        session.last_sent_at = time.time()
        await self.store.save_signup_session(data.session_id, session)
        await self.store.incr_daily("signup", email)
        await self.notifier.send_verification_code(email, code)
        return SignUpResult(session_id=data.session_id, retry_after=cooldown_for(1))

    # --- sign-in / refresh -------------------------------------------------
    async def sign_in(self, data: SignInDto) -> TokenPair:
        user = await self.users.get_by_email(data.email)
        if user is None or not self.hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.email_verified or not user.is_active:
            raise EmailNotVerifiedError()
        return await self.tokens.issue_pair(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        claims = self.tokens.verify_refresh(refresh_token)
        user = await self.users.get_by_id(claims.sub)
        if user is None:
            raise InvalidRefreshTokenError()
        if not user.is_active:
            raise InactiveUserError()
        return await self.tokens.rotate(claims, user)

    async def sign_out(self, refresh_token: str | None) -> None:
        # Revoke the current session's refresh token; cookies are cleared by the
        # router. A missing/invalid token is a no-op so logout is idempotent.
        if refresh_token:
            await self.tokens.revoke(refresh_token)

    # --- password reset ----------------------------------------------------
    async def request_password_reset(self, data: RequestResetDto) -> int | None:
        return await self._dispatch_reset(data.email)

    async def resend_reset_link(self, data: RequestResetDto) -> int | None:
        return await self._dispatch_reset(data.email)

    async def _dispatch_reset(self, email: str) -> int | None:
        """Issue (or throttle) a password-reset link; returns seconds until the
        next send is allowed, or None when the account does not exist.

        Shared by the request and resend endpoints: the first call sends a link,
        subsequent calls are subject to the escalating cooldown and daily cap and
        invalidate the previous token when a new one is issued.
        """
        user = await self.users.get_by_email(email)
        if user is None:
            return None  # silent OK, do not reveal whether the account exists
        norm = user.email.value

        if await self.store.daily_count("reset", norm) >= DAILY_SEND_LIMIT:
            raise DailySendLimitExceededError()

        rsession = await self.store.get_reset_session(norm)
        if rsession is None:
            return await self._issue_reset(user.require_id, norm, send_count=1)

        remaining = self._cooldown_remaining(rsession.send_count, rsession.last_sent_at)
        if remaining > 0:
            # Still cooling down: report the wait, don't issue a new link.
            return remaining

        await self.store.delete_reset_token(rsession.token)  # invalidate old link
        return await self._issue_reset(
            user.require_id, norm, send_count=rsession.send_count + 1
        )

    async def verify_reset_token(self, token: str) -> None:
        if await self.store.get_reset_token(token) is None:
            raise InvalidResetVerificationTokenError()

    async def confirm_password_reset(self, data: ConfirmResetDto) -> None:
        record = await self.store.get_reset_token(data.reset_token)
        if record is None:
            raise InvalidResetVerificationTokenError()
        user = await self.users.get_by_id(record.user_id)
        if user is None:
            raise InvalidResetVerificationTokenError()

        user.set_password(self.hasher.hash(data.new_password))
        await self.users.update(user)
        await self.store.delete_reset_token(data.reset_token)
        await self.tokens.revoke_all(user.require_id)  # force re-login everywhere

    # --- helpers -----------------------------------------------------------
    @staticmethod
    def _generate_otp() -> int:
        return secrets.randbelow(900_000) + 100_000  # always 6 digits

    @staticmethod
    def _cooldown_remaining(send_count: int, last_sent_at: float) -> int:
        remaining = cooldown_for(send_count) - (time.time() - last_sent_at)
        return max(0, math.ceil(remaining))

    def _reset_link(self, token: str) -> str:
        base = str(settings.APP_URL).rstrip("/")
        return f"{base}/reset-password?token={token}"

    async def _issue_reset(self, user_id: int, email: str, send_count: int) -> int:
        token = secrets.token_urlsafe(32)
        await self.store.save_reset_token(
            token, ResetToken(user_id=user_id, email=email)
        )
        await self.store.save_reset_session(
            email,
            ResetSession(token=token, send_count=send_count, last_sent_at=time.time()),
        )
        await self.store.incr_daily("reset", email)
        await self.notifier.send_reset_link(email, self._reset_link(token))
        return cooldown_for(send_count)
