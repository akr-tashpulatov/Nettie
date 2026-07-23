from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import SessionStatus, WritingTaskModule, WritingTaskType


class WritingTopicModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "writing_topics"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    tasks: Mapped[list["WritingTaskModel"]] = relationship(back_populates="topic")
    sessions: Mapped[list["WritingSessionModel"]] = relationship(back_populates="topic")


class WritingTaskModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "writing_tasks"

    __table_args__ = (
        Index(
            "uq_writing_tasks_topic_order",
            "topic_id",
            "order_index",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("writing_topics.id"), nullable=False
    )
    module: Mapped[WritingTaskModule] = mapped_column(nullable=False)
    task_type: Mapped[WritingTaskType] = mapped_column(nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("media.id"), nullable=True
    )
    order_index: Mapped[int] = mapped_column(nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    topic: Mapped["WritingTopicModel"] = relationship(back_populates="tasks")
    answers: Mapped[list["WritingAnswerModel"]] = relationship(back_populates="task")


class WritingSessionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "writing_sessions"

    __table_args__ = (
        Index("ix_writing_sessions_user_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("writing_topics.id"), nullable=False
    )
    module: Mapped[WritingTaskModule] = mapped_column(nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        nullable=False, default=SessionStatus.IN_PROGRESS
    )
    overall_band: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    topic: Mapped["WritingTopicModel"] = relationship(back_populates="sessions")
    answers: Mapped[list["WritingAnswerModel"]] = relationship(back_populates="session")


class WritingAnswerModel(Base, IdMixin):
    __tablename__ = "writing_answers"

    __table_args__ = (
        UniqueConstraint(
            "session_id", "task_id", name="uq_writing_answers_session_task"
        ),
    )

    task_id: Mapped[int] = mapped_column(ForeignKey("writing_tasks.id"), nullable=False)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("writing_sessions.id"), nullable=False
    )

    essay_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(nullable=False)
    task_achievement: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    coherence_cohesion: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    lexical_resource: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    grammatical_range_accuracy: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    overall_band: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    feedback: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_annotations: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    time_spent_sec: Mapped[int] = mapped_column(nullable=False)

    task: Mapped["WritingTaskModel"] = relationship(back_populates="answers")
    session: Mapped["WritingSessionModel"] = relationship(back_populates="answers")
