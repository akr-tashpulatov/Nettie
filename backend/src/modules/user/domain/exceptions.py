from src.core.domain import (
    AuthorizationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


class UserNotFoundError(NotFoundError):
    """User not found."""


class EmailAlreadyExistsError(ConflictError):
    """Email already exists."""


class PhoneNumberAlreadyExistsError(ConflictError):
    """Phone number already exists."""


class UserAlreadyActiveError(ConflictError):
    """User is already active."""


class UserAlreadyInactiveError(ConflictError):
    """User is already inactive."""


class EmailChangeNotAllowedError(AuthorizationError):
    """Only administrators can change an email address."""


class InvalidCurrentPasswordError(BadRequestError):
    """Current password is incorrect."""


class PasswordUnchangedError(BadRequestError):
    """New password must differ from the current password."""


class InvalidEmailError(ValidationError):
    """Invalid email address."""


class InvalidPhoneNumberError(ValidationError):
    """Invalid phone number."""
