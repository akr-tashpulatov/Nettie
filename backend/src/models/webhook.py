from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base, IdMixin


class WebhookEventModel(Base, IdMixin):
    __tablename__ = "webhook_events"

    __table_args__ = (
        UniqueConstraint(
            "provider", "external_event_id", name="uq_webhook_provider_event"
        ),
    )

    provider: Mapped[str] = mapped_column(nullable=False)
    external_event_id: Mapped[str] = mapped_column(nullable=False)
    transaction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transactions.id"), nullable=True
    )
    signature_valid: Mapped[bool] = mapped_column(nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
