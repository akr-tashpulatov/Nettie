from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin
from src.models.enums import ProcessingStatus, SessionStatus, SpeakingPart

_processing_status_enum = Enum(
    ProcessingStatus, name="processingstatus", create_type=False
)


class SpeakingTopicModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "speaking_topics"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    questions: Mapped[list["SpeakingQuestionModel"]] = relationship(
        back_populates="topic"
    )
    sessions: Mapped[list["SpeakingSessionModel"]] = relationship(
        back_populates="topic"
    )


class SpeakingQuestionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "speaking_questions"

    __table_args__ = (
        Index(
            "uq_speaking_questions_topic_part_order",
            "topic_id",
            "part",
            "order_index",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("speaking_topics.id"), nullable=False
    )
    part: Mapped[SpeakingPart] = mapped_column(nullable=False)
    question_text: Mapped[str] = mapped_column(nullable=False)
    order_index: Mapped[int] = mapped_column(nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    topic: Mapped["SpeakingTopicModel"] = relationship(back_populates="questions")
    answers: Mapped[list["SpeakingAnswerModel"]] = relationship(
        back_populates="question"
    )


class SpeakingSessionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "speaking_sessions"

    __table_args__ = (
        Index("ix_speaking_sessions_user_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("speaking_topics.id"), nullable=False
    )
    status: Mapped[SessionStatus] = mapped_column(
        nullable=False, default=SessionStatus.IN_PROGRESS
    )
    score_fluency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    score_vocabulary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    score_grammar: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    score_pronunciation: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    overall_band: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    feedback: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    topic: Mapped["SpeakingTopicModel"] = relationship(back_populates="sessions")
    answers: Mapped[list["SpeakingAnswerModel"]] = relationship(
        back_populates="session"
    )


class SpeakingAnswerModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "speaking_answers"

    __table_args__ = (
        UniqueConstraint(
            "session_id", "question_id", name="uq_speaking_answers_session_question"
        ),
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("speaking_sessions.id"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("speaking_questions.id"), nullable=False
    )
    audio_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    order_index: Mapped[int] = mapped_column(nullable=False)
    stt_status: Mapped[ProcessingStatus] = mapped_column(
        _processing_status_enum, nullable=False, default=ProcessingStatus.PENDING
    )
    pronunciation_assessment_status: Mapped[ProcessingStatus] = mapped_column(
        _processing_status_enum, nullable=False, default=ProcessingStatus.PENDING
    )
    transcript: Mapped[Optional[str]] = mapped_column(nullable=True)
    corrections: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    pronunciation_assessment_result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )

    session: Mapped["SpeakingSessionModel"] = relationship(back_populates="answers")
    question: Mapped["SpeakingQuestionModel"] = relationship(back_populates="answers")
