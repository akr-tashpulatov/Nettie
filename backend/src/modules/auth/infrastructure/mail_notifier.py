from src.modules.mail.application.tasks import (
    send_reset_password_mail_task,
    send_verify_account_mail_task,
)


class TaskiqMailNotifier:
    """IMailNotifier implementation that enqueues TaskIQ mail tasks.

    The HTTP request returns immediately; the mail worker performs the SMTP send.
    """

    async def send_verification_code(self, email: str, code: int) -> None:
        await send_verify_account_mail_task.kiq(email, code)

    async def send_reset_link(self, email: str, link: str) -> None:
        await send_reset_password_mail_task.kiq(email, link)
