from src.core.domain import NotFoundError, ValidationError


class MediaNotFoundError(NotFoundError):
    """Media not found."""


class InvalidMediaTypeError(ValidationError):
    """Unsupported file type."""


class MediaTooLargeError(ValidationError):
    """The uploaded file exceeds the maximum allowed size."""


class EmptyMediaError(ValidationError):
    """The uploaded file is empty."""
