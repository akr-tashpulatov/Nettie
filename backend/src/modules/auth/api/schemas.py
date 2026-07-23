from typing import Literal

from pydantic import BaseModel, EmailStr

from src.core.validators import Password, PhoneNumber


class SignUpRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: PhoneNumber
    password: Password


class SignUpResponse(BaseModel):
    session_id: str
    retry_after: int


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    access_token: str
    refresh_token: str


class ResendCodeRequest(BaseModel):
    session_id: str


class ResendCodeResponse(BaseModel):
    session_id: str
    retry_after: int


class ChangeSignUpEmailRequest(BaseModel):
    session_id: str
    email: EmailStr


class SignUpVerifyRequest(BaseModel):
    otp_code: int
    session_id: str


class SignUpVerifyResponse(BaseModel):
    success: bool
    code_invalidated: bool = False
    access_token: str | None = None
    refresh_token: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str


class SignOutResponse(BaseModel):
    status: Literal["OK"] = "OK"


class RequestPasswordResetRequest(BaseModel):
    email: EmailStr


class RequestPasswordResetResponse(BaseModel):
    status: Literal["OK"] = "OK"
    retry_after: int = 0


class VerifyPasswordResetRequest(BaseModel):
    reset_token: str


class VerifyPasswordResetResponse(BaseModel):
    status: Literal["OK"] = "OK"


class ResendResetLinkRequest(BaseModel):
    email: EmailStr


class ResendResetLinkResponse(BaseModel):
    status: Literal["OK"] = "OK"
    retry_after: int = 0


class ConfirmPasswordResetRequest(BaseModel):
    reset_token: str
    new_password: Password


class ConfirmPasswordResetResponse(BaseModel):
    status: Literal["OK"] = "OK"
