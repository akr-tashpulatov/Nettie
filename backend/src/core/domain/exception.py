class DomainException(Exception):
    """Base class for all domain errors.

    The exception's docstring is used as the default client-facing message,
    so subclasses should keep their docstring short and user-safe.
    """

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or (self.__doc__ or "").strip()
        super().__init__(self.detail)


class BadRequestError(DomainException):
    """The request is malformed or semantically invalid."""


class ValidationError(BadRequestError):
    """A domain invariant was violated."""


class AuthenticationError(DomainException):
    """Authentication is required or the provided credentials are invalid."""


class AuthorizationError(DomainException):
    """The caller is not allowed to perform this action."""


class NotFoundError(DomainException):
    """Requested resource was not found."""


class ConflictError(DomainException):
    """Operation conflicts with the current state of the resource."""


class RateLimitError(DomainException):
    """Too many requests; the caller must slow down or retry later."""


class ServiceUnavailableError(DomainException):
    """An upstream dependency is unavailable; the caller should retry later."""
