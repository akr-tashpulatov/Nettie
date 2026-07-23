from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base, IdMixin, TimestampMixin


class TestModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "tests"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    mode: Mapped[int] = mapped_column()
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)


class QuestionModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "questions"

    test_id: Mapped[int] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"), index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column()

    options: Mapped[list["OptionModel"]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )


class OptionModel(Base, IdMixin):
    __tablename__ = "question_options"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(default=False)
    position: Mapped[int] = mapped_column()
