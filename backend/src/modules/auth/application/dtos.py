from dataclasses import dataclass

from pydantic import BaseModel, EmailStr

from src.core.validators import Password, PhoneNumber
from src.models.enums import Role


@dataclass(frozen=True)
class TokenPair:
    expires_in: int
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class AccessTokenClaims:
    """Authenticated principal decoded from a verified access token."""

    sub: int
    role: Role
    email: str
    full_name: str
    phone_number: str | None = None


@dataclass(frozen=True)
class RefreshTokenClaims:
    """Identity decoded from a verified refresh token.

    ``jti`` is the token's entry in the per-user allowlist; rotation consumes it.
    """

    sub: int
    jti: str


@dataclass(frozen=True)
class SignUpResult:
    session_id: str
    retry_after: int


@dataclass(frozen=True)
class VerifyResult:
    success: bool
    code_invalidated: bool = False
    tokens: TokenPair | None = None


class SignUpDto(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: PhoneNumber
    password: Password


class VerifyOtpDto(BaseModel):
    session_id: str
    otp_code: int


class ChangeSignUpEmailDto(BaseModel):
    session_id: str
    email: EmailStr


class SignInDto(BaseModel):
    email: EmailStr
    password: str


class RequestResetDto(BaseModel):
    email: EmailStr


class ConfirmResetDto(BaseModel):
    reset_token: str
    new_password: Password
