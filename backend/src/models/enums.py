import enum


class Role(enum.Enum):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"


class TestMode(enum.IntEnum):
    """Number of questions drawn for a single test session."""

    THIRTY = 30
    FORTY = 40


class SessionStatus(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
