from typing import Protocol


class IMailNotifier(Protocol):
    """Port the service uses to dispatch emails without knowing about the broker.

    The infrastructure implementation enqueues TaskIQ tasks that the mail worker
    consumes, so HTTP requests never block on SMTP.
    """

    async def send_verification_code(self, email: str, code: int) -> None: ...

    async def send_reset_link(self, email: str, link: str) -> None: ...
