from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AuditLogModel

from .context import get_actor


class SQLAlchemyAuditLogger:
    """Implements IAuditLogger on the request's session, so the audit row
    commits (or rolls back) atomically with the change it describes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log(
        self,
        *,
        action: str,
        entity: str,
        entity_id: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> None:
        actor = get_actor()
        if actor is None or actor.user_id is None:
            raise RuntimeError(
                "Audit log requested without an authenticated actor; "
                "the route is missing an auth guard."
            )
        self.session.add(
            AuditLogModel(
                actor_id=actor.user_id,
                action=action,
                entity=entity,
                entity_id=entity_id,
                before=before,
                after=after,
                ip=actor.ip,
                user_agent=actor.user_agent,
                request_id=actor.request_id,
            )
        )
