import re
from dataclasses import dataclass

from src.core.validators import validate_kz_phone

from .exceptions import InvalidEmailError, InvalidPhoneNumberError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    """An email address. Validated on creation; immutable thereafter."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmailError(f"Invalid email address: {self.value!r}")
        # frozen dataclass: bypass the immutability guard to store the normalized form
        object.__setattr__(self, "value", normalized)

    @classmethod
    def from_trusted(cls, value: str) -> "Email":
        """Rebuild from an already-validated source (e.g. the database) without re-validating."""
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", value)
        return obj

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PhoneNumber:
    """A KZ phone number stored in E.164 form. Validated on creation."""

    value: str

    def __post_init__(self) -> None:
        try:
            normalized = validate_kz_phone(self.value)
        except ValueError as exc:
            raise InvalidPhoneNumberError(str(exc)) from exc
        object.__setattr__(self, "value", normalized)

    @classmethod
    def from_trusted(cls, value: str) -> "PhoneNumber":
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", value)
        return obj

    def __str__(self) -> str:
        return self.value
