from datetime import datetime
from decimal import Decimal

from src.core.broker import broker
from src.modules.mail.application.dtos import (
    PasswordResetMailDto,
    SubscriptionSuccessMailDto,
    VerifyAccountMailDto,
)
from src.modules.mail.application.mail_service import MailService

_mail_service = MailService()


@broker.task
async def send_verify_account_mail_task(email: str, code: int) -> None:
    """Render and deliver the account-verification OTP email (runs in the worker)."""
    await _mail_service.send_verify_account_mail(
        email, VerifyAccountMailDto(code=code, email=email)
    )


@broker.task
async def send_reset_password_mail_task(email: str, reset_link: str) -> None:
    """Render and deliver the password-reset link email (runs in the worker)."""
    await _mail_service.send_reset_password_mail(
        email, PasswordResetMailDto.model_validate({"reset_link": reset_link})
    )


@broker.task
async def send_subscription_success_mail_task(
    email: str, full_name: str, amount: str, currency: str, valid_until: str
) -> None:
    """Render and deliver the subscription payment-success email (runs in the worker)."""
    await _mail_service.send_subscription_success_mail(
        email,
        SubscriptionSuccessMailDto(
            full_name=full_name,
            amount=Decimal(amount),
            currency=currency,
            valid_until=datetime.fromisoformat(valid_until),
        ),
    )
