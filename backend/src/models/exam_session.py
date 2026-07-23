from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import SessionStatus


class TestSessionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "test_sessions"

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    status: Mapped[SessionStatus] = mapped_column(default=SessionStatus.IN_PROGRESS)
    total: Mapped[int] = mapped_column()
    correct_count: Mapped[int] = mapped_column(default=0)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items: Mapped[list["SessionItemModel"]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )


class SessionItemModel(Base, IdMixin):
    __tablename__ = "session_items"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("test_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    position: Mapped[int] = mapped_column()
    selected_option_id: Mapped[int | None] = mapped_column(
        ForeignKey("question_options.id"), nullable=True
    )
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
