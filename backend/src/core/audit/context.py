from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuditActor:
    user_id: Optional[int]
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None


_actor: ContextVar[AuditActor | None] = ContextVar("audit_actor", default=None)


def set_actor(actor: AuditActor | None) -> None:
    _actor.set(actor)


def get_actor() -> AuditActor | None:
    return _actor.get()
