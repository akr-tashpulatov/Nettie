from typing import Any, Protocol


class IAuditLogger(Protocol):
    """Port for recording admin actions. The implementation resolves the actor
    (who / from where) from the request context set by the auth guard; callers
    only describe what happened in business terms."""

    async def log(
        self,
        *,
        action: str,
        entity: str,
        entity_id: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> None: ...
