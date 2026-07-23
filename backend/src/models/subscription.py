from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import SubscriptionStatus

if TYPE_CHECKING:
    from src.models.tariff import TariffModel
    from src.models.user import UserModel


class SubscriptionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    # One "live" subscription per user; unlimited CANCELED history is allowed
    # since a plain unique(user_id, status) would block a user's second cancel.
    __table_args__ = (
        Index(
            "uq_subscription_user_live",
            "user_id",
            unique=True,
            postgresql_where=text("status IN ('PENDING','ACTIVE','PAST_DUE')"),
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["UserModel"] = relationship(back_populates="subscriptions")
    tariff: Mapped["TariffModel"] = relationship(back_populates="subscriptions")
