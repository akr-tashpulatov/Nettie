from typing import Any, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base, IdMixin, TimestampMixin


class AuditLogModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_actor_created", "actor_id", "created_at"),
        Index("ix_audit_logs_entity", "entity", "entity_id"),
    )

    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    entity: Mapped[str] = mapped_column(nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    before: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    after: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String, default=None)
    user_agent: Mapped[Optional[str]] = mapped_column(String, default=None)
    request_id: Mapped[Optional[str]] = mapped_column(String, default=None)
