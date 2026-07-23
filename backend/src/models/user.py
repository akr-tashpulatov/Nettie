from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import Role


class UserModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[Role] = mapped_column()
    password_hash: Mapped[str] = mapped_column()
    email_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
