from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base, IdMixin, TimestampMixin


class MediaModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "media"

    object_bucket: Mapped[str] = mapped_column(nullable=False)
    object_key: Mapped[str] = mapped_column(nullable=False, unique=True)
    size: Mapped[int] = mapped_column(nullable=False)
    extension: Mapped[str] = mapped_column(nullable=False)
    mimetype: Mapped[str] = mapped_column(nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
