from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin
from src.models.enums import DurationUnit

if TYPE_CHECKING:
    from src.models.subscription import SubscriptionModel


class ServiceModel(Base, IdMixin):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)

    tariff_items: Mapped[list["TariffItemModel"]] = relationship(
        back_populates="service"
    )


class TariffModel(Base, IdMixin):
    __tablename__ = "tariffs"

    name: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="KZT", server_default="KZT"
    )
    discount_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    duration: Mapped[int] = mapped_column(nullable=False)
    duration_unit: Mapped[DurationUnit] = mapped_column(nullable=False)

    items: Mapped[list["TariffItemModel"]] = relationship(back_populates="tariff")
    subscriptions: Mapped[list["SubscriptionModel"]] = relationship(
        back_populates="tariff"
    )


class TariffItemModel(Base, IdMixin):
    __tablename__ = "tariff_items"

    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)

    tariff: Mapped["TariffModel"] = relationship(back_populates="items")
    service: Mapped["ServiceModel"] = relationship(back_populates="tariff_items")
