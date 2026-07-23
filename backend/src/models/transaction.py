from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import DurationUnit, PaymentMethod, TransactionStatus

if TYPE_CHECKING:
    from src.models.subscription import SubscriptionModel
    from src.models.tariff import TariffModel
    from src.models.user import UserModel


class TransactionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "transactions"

    invoice_id: Mapped[str] = mapped_column(
        String(6),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"), nullable=False)
    subscription_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("subscriptions.id"), nullable=True
    )
    provider: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    # Duration cold-saved from the tariff at initiation, so a later change to the
    # tariff can't alter the subscription window this payment already paid for.
    tariff_duration: Mapped[int] = mapped_column(nullable=False)
    duration_unit: Mapped[DurationUnit] = mapped_column(nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # The provider's payment id (Halyk webhook `id` field); needed for refunds.
    external_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, index=True
    )

    user: Mapped["UserModel"] = relationship(back_populates="transactions")
    tariff: Mapped["TariffModel"] = relationship()
    subscription: Mapped["SubscriptionModel"] = relationship()
