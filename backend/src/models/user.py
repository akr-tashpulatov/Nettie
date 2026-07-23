from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import Role

if TYPE_CHECKING:
    from src.models.subscription import SubscriptionModel
    from src.models.transaction import TransactionModel


class UserModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[Role] = mapped_column()
    password_hash: Mapped[str] = mapped_column()
    email_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    study_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("study_groups.id"), nullable=True, index=True
    )

    subscriptions: Mapped[list["SubscriptionModel"]] = relationship(
        back_populates="user"
    )
    transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="user")
