import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class IdMixin:
    """Mixin for autoincrement integer primary key."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Mixin for created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
