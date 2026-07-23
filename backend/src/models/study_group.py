from datetime import date

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base, IdMixin, TimestampMixin


class StudyGroupModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "study_groups"

    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    starts_at: Mapped[date] = mapped_column(Date, nullable=False)
    enrollment_open: Mapped[bool] = mapped_column(
        default=True, server_default="true", nullable=False
    )
