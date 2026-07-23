from src.core.domain import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
)


class InvalidOtpCodeError(AuthenticationError):
    """Invalid or expired OTP code."""


class InvalidResetVerificationTokenError(AuthenticationError):
    """Invalid or expired reset verification token."""


class TooManySignInAttemptsError(RateLimitError):
    """Too many sign-in attempts. Try again later."""


class TooManyResetVerificationRetriesError(RateLimitError):
    """Too many verification retries. Try again later."""


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password."""


class EmailNotVerifiedError(AuthenticationError):
    """Email address is not verified."""


class InvalidRefreshTokenError(AuthenticationError):
    """Invalid or expired refresh token."""


class InvalidAccessTokenError(AuthenticationError):
    """Missing, invalid or expired access token."""


class InsufficientRoleError(AuthorizationError):
    """The authenticated user's role is not allowed to access this resource."""


class InactiveUserError(AuthorizationError):
    """The account is deactivated."""


class SignUpSessionExpiredError(NotFoundError):
    """Sign-up session not found or expired."""


class DailySendLimitExceededError(RateLimitError):
    """Daily email sending limit reached. Try again tomorrow."""
