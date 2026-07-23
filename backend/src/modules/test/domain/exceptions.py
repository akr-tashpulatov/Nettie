from src.core.domain import ConflictError, NotFoundError, ValidationError


class TestNotFoundError(NotFoundError):
    """Test not found."""


class QuestionNotFoundError(NotFoundError):
    """Question not found."""


class InvalidQuestionError(ValidationError):
    """A question must have at least two options and exactly one correct answer."""


class EmptyDocxError(ValidationError):
    """The uploaded document contains no questions."""


class InvalidDocxError(ValidationError):
    """The uploaded document is not a valid .docx file or is malformed."""


class TestNameAlreadyExistsError(ConflictError):
    """A test with this name already exists."""
