from src.core.domain import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)


class SessionNotFoundError(NotFoundError):
    """Test session not found."""


class TestNotFoundError(NotFoundError):
    """Test not found."""


class TestNotEligibleError(ValidationError):
    """This test does not have enough questions to start a session."""


class InvalidOptionError(ValidationError):
    """The selected option does not belong to this question."""


class QuestionNotInSessionError(NotFoundError):
    """This question is not part of the session."""


class QuestionAlreadyAnsweredError(ConflictError):
    """This question has already been answered in this session."""


class SessionCompletedError(ConflictError):
    """This session is already completed."""


class SessionForbiddenError(AuthorizationError):
    """This session belongs to another student."""


class QuestionNotFoundError(NotFoundError):
    """Question not found."""


class ExplanationUnavailableError(ServiceUnavailableError):
    """The AI explanation could not be generated. Please try again later."""
