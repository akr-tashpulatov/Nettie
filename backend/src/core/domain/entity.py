from dataclasses import dataclass
from datetime import datetime


class EntityNotPersistedError(RuntimeError):
    """A persistence-derived field (`id`, `created_at`) was read before the
    entity was persisted. This is a programming error, not a client error, so
    it deliberately does not subclass `DomainException` — it must surface as a
    500, not be mapped to a 4xx.
    """


@dataclass(kw_only=True)
class Entity:
    """Base for aggregate roots with a DB-assigned primary key.

    `id` is None until the repository persists the entity (see
    `.claude/rules/repository.md`). Call sites that only ever see an
    already-persisted instance — fetched from a repository, or returned by
    `add`/`update` — should use `require_id` instead of re-deriving the same
    narrowing with a bare `assert` or a `type: ignore[arg-type]`.
    """

    id: int | None = None

    @property
    def require_id(self) -> int:
        if self.id is None:
            raise EntityNotPersistedError(f"{type(self).__name__} has no id yet")
        return self.id


@dataclass(kw_only=True)
class TimestampedEntity(Entity):
    """`Entity` for aggregates whose `created_at` is also filled in on
    persistence (by the repository, or by a factory method that stamps the
    creation time itself) rather than known upfront.

    Use `require_created_at` the same way as `require_id`.
    """

    created_at: datetime | None = None

    @property
    def require_created_at(self) -> datetime:
        if self.created_at is None:
            raise EntityNotPersistedError(
                f"{type(self).__name__} has no created_at yet"
            )
        return self.created_at
