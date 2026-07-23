from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.config import settings
from src.core.logger import logging
from src.modules.mail.application.dtos import (
    PasswordResetMailDto,
    SubscriptionSuccessMailDto,
    VerifyAccountMailDto,
)

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class MailService:
    def __init__(self):
        self.jinja2_env = Environment(
            loader=FileSystemLoader(_TEMPLATES_DIR),
            autoescape=select_autoescape(enabled_extensions=("html")),
        )
        self.verify_account_template = self.jinja2_env.get_template(
            "verify_account.html"
        )
        self.password_reset_template = self.jinja2_env.get_template(
            "password_reset.html"
        )
        self.subscription_success_template = self.jinja2_env.get_template(
            "subscription_success.html"
        )

    async def send_verify_account_mail(self, to: str, data: VerifyAccountMailDto):
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        message["To"] = to
        message["Subject"] = f"Verify {settings.APP_NAME} account"

        verify_account_html = self.verify_account_template.render(**data.model_dump())

        html_msg = MIMEText(verify_account_html, "html")

        message.attach(html_msg)

        await self.send_message(message)

    async def send_reset_password_mail(self, to: str, data: PasswordResetMailDto):
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        message["To"] = to
        message["Subject"] = f"Reset {settings.APP_NAME} account password"

        password_reset_html = self.password_reset_template.render(**data.model_dump())

        html_msg = MIMEText(password_reset_html, "html")

        message.attach(html_msg)

        await self.send_message(message)

    async def send_subscription_success_mail(
        self, to: str, data: SubscriptionSuccessMailDto
    ):
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        message["To"] = to
        message["Subject"] = f"Your {settings.APP_NAME} payment was successful"

        subscription_success_html = self.subscription_success_template.render(
            **data.model_dump()
        )

        html_msg = MIMEText(subscription_success_html, "html")

        message.attach(html_msg)

        await self.send_message(message)

    async def send_message(self, message: EmailMessage | MIMEMultipart):
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.MAIL_SERVER,
                port=settings.MAIL_PORT,
                username=settings.MAIL_USERNAME,
                password=settings.MAIL_PASSWORD,
                start_tls=settings.MAIL_STARTTLS,
                use_tls=settings.MAIL_SSL_TLS,
            )
        except Exception:
            logging.error("Failed to send mail message", exc_info=True)
            raise
