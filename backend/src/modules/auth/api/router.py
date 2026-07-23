from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from src.core.cookie.cookie_service import CookieService
from src.core.exceptions import error_responses
from src.modules.user.domain.exceptions import (
    EmailAlreadyExistsError,
    PhoneNumberAlreadyExistsError,
)

from ..application.dtos import (
    ChangeSignUpEmailDto,
    ConfirmResetDto,
    RequestResetDto,
    SignInDto,
    SignUpDto,
    VerifyOtpDto,
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
from .cookies import (
    REFRESH_TOKEN_COOKIE,
    clear_auth_cookies,
    get_cookie_service,
    set_auth_cookies,
)
from .dependencies import AuthService, get_auth_service
from .schemas import (
    ChangeSignUpEmailRequest,
    ConfirmPasswordResetRequest,
    ConfirmPasswordResetResponse,
    RefreshRequest,
    RefreshResponse,
    RequestPasswordResetRequest,
    RequestPasswordResetResponse,
    ResendCodeRequest,
    ResendCodeResponse,
    ResendResetLinkRequest,
    ResendResetLinkResponse,
    SignInRequest,
    SignInResponse,
    SignOutResponse,
    SignUpRequest,
    SignUpResponse,
    SignUpVerifyRequest,
    SignUpVerifyResponse,
    VerifyPasswordResetRequest,
    VerifyPasswordResetResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/sign-in",
    response_model=SignInResponse,
    summary="Sign in with email and password",
    description="Authenticates a user and issues an access/refresh token pair, "
    "setting the refresh token as an HTTP-only cookie.",
    responses=error_responses(InvalidCredentialsError, EmailNotVerifiedError),
)
async def sign_in(
    payload: SignInRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    cookies: Annotated[CookieService, Depends(get_cookie_service)],
) -> SignInResponse:
    tokens = await service.sign_in(SignInDto(**payload.model_dump()))
    set_auth_cookies(cookies, response, tokens)
    return SignInResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post(
    "/sign-up",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start sign-up with email/phone verification",
    description="Creates a pending sign-up session and sends an OTP code to the "
    "given email. The account is only created once the code is verified via "
    "`/sign-up/verify`.",
    responses=error_responses(EmailAlreadyExistsError, PhoneNumberAlreadyExistsError),
)
async def sign_up(
    payload: SignUpRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SignUpResponse:
    result = await service.sign_up(SignUpDto(**payload.model_dump()))
    return SignUpResponse(session_id=result.session_id, retry_after=result.retry_after)


@router.post(
    "/sign-up/resend-code",
    response_model=ResendCodeResponse,
    summary="Resend the sign-up OTP code",
    description="Resends the verification code for a pending sign-up session, "
    "subject to the daily send limit.",
    responses=error_responses(SignUpSessionExpiredError, DailySendLimitExceededError),
)
async def resend_code(
    payload: ResendCodeRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ResendCodeResponse:
    result = await service.resend_code(payload.session_id)
    return ResendCodeResponse(
        session_id=result.session_id, retry_after=result.retry_after
    )


@router.post(
    "/sign-up/change-email",
    response_model=SignUpResponse,
    summary="Change the email for a pending sign-up",
    description="Updates the email on a pending sign-up session and resends the "
    "OTP code to the new address.",
    responses=error_responses(
        SignUpSessionExpiredError, DailySendLimitExceededError, EmailAlreadyExistsError
    ),
)
async def change_signup_email(
    payload: ChangeSignUpEmailRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SignUpResponse:
    result = await service.change_signup_email(
        ChangeSignUpEmailDto(**payload.model_dump())
    )
    return SignUpResponse(session_id=result.session_id, retry_after=result.retry_after)


@router.post(
    "/sign-up/verify",
    response_model=SignUpVerifyResponse,
    summary="Verify the sign-up OTP code",
    description="Confirms the OTP code for a pending sign-up session, creates the "
    "account, and — on success — signs the user in by setting auth cookies.",
    responses=error_responses(SignUpSessionExpiredError),
)
async def sign_up_verify(
    payload: SignUpVerifyRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    cookies: Annotated[CookieService, Depends(get_cookie_service)],
) -> SignUpVerifyResponse:
    result = await service.verify(VerifyOtpDto(**payload.model_dump()))
    tokens = result.tokens
    if tokens is not None:
        set_auth_cookies(cookies, response, tokens)
    return SignUpVerifyResponse(
        success=result.success,
        code_invalidated=result.code_invalidated,
        access_token=tokens.access_token if tokens else None,
        refresh_token=tokens.refresh_token if tokens else None,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh access and refresh tokens",
    description="Exchanges a valid refresh token for a new access/refresh token "
    "pair, rotating the refresh token cookie.",
    responses=error_responses(InvalidRefreshTokenError, InactiveUserError),
)
async def refresh(
    payload: RefreshRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    cookies: Annotated[CookieService, Depends(get_cookie_service)],
) -> RefreshResponse:
    tokens = await service.refresh(payload.refresh_token)
    set_auth_cookies(cookies, response, tokens)
    return RefreshResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post(
    "/sign-out",
    response_model=SignOutResponse,
    summary="Sign out",
    description="Revokes the current refresh token and clears the auth cookies.",
)
async def sign_out(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    cookies: Annotated[CookieService, Depends(get_cookie_service)],
) -> SignOutResponse:
    refresh_token = cookies.get_cookie(request, REFRESH_TOKEN_COOKIE)
    await service.sign_out(refresh_token)
    clear_auth_cookies(cookies, response)
    return SignOutResponse()


@router.post(
    "/reset-password/request",
    response_model=RequestPasswordResetResponse,
    summary="Request a password reset link",
    description="Sends a password reset link to the given email if an account "
    "exists for it, subject to the daily send limit.",
    responses=error_responses(DailySendLimitExceededError),
)
async def request_reset_password(
    payload: RequestPasswordResetRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> RequestPasswordResetResponse:
    retry_after = await service.request_password_reset(
        RequestResetDto(**payload.model_dump())
    )
    return RequestPasswordResetResponse(retry_after=retry_after or 0)


@router.post(
    "/reset-password/resend",
    response_model=ResendResetLinkResponse,
    summary="Resend the password reset link",
    description="Resends the password reset link for the given email, subject "
    "to the daily send limit.",
    responses=error_responses(DailySendLimitExceededError),
)
async def resend_reset_password(
    payload: ResendResetLinkRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ResendResetLinkResponse:
    retry_after = await service.resend_reset_link(
        RequestResetDto(**payload.model_dump())
    )
    return ResendResetLinkResponse(retry_after=retry_after or 0)


@router.post(
    "/reset-password/verify",
    response_model=VerifyPasswordResetResponse,
    summary="Verify a password reset token",
    description="Checks that a password reset token is valid and unexpired, "
    "without consuming it, so the client can show the reset form.",
    responses=error_responses(InvalidResetVerificationTokenError),
)
async def verify_reset_password(
    payload: VerifyPasswordResetRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> VerifyPasswordResetResponse:
    await service.verify_reset_token(payload.reset_token)
    return VerifyPasswordResetResponse()


@router.post(
    "/reset-password/confirm",
    response_model=ConfirmPasswordResetResponse,
    summary="Confirm a password reset",
    description="Consumes the reset token and sets the new password on the account.",
    responses=error_responses(InvalidResetVerificationTokenError),
)
async def confirm_reset_password(
    payload: ConfirmPasswordResetRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ConfirmPasswordResetResponse:
    await service.confirm_password_reset(ConfirmResetDto(**payload.model_dump()))
    return ConfirmPasswordResetResponse()
