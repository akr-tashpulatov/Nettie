from decimal import Decimal

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import DurationUnit


class RenewalSettingsModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "renewal_settings"
    __table_args__ = (CheckConstraint("id = 1", name="ck_renewal_settings_singleton"),)

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="KZT", server_default="KZT"
    )
    duration: Mapped[int] = mapped_column(nullable=False)
    duration_unit: Mapped[DurationUnit] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    @declared_attr.directive
    def __mapper_args__(cls) -> dict:
        return {"version_id_col": cls.version}
