import enum


class Role(enum.Enum):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"


class SubscriptionStatus(enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"


class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(enum.Enum):
    CARD = "CARD"


class DurationUnit(enum.Enum):
    HOURS = "HOURS"
    DAYS = "DAYS"
    MONTHS = "MONTHS"


class WritingTaskModule(enum.Enum):
    ACADEMIC = "ACADEMIC"
    GENERAL = "GENERAL"


class WritingTaskType(enum.IntEnum):
    TASK_1 = 1
    TASK_2 = 2


class SessionStatus(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    SCORING = "SCORING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class ProcessingStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class SpeakingPart(enum.IntEnum):
    PART_1 = 1
    PART_2 = 2
    PART_3 = 3
