from dataclasses import dataclass

from src.core.domain import TimestampedEntity
from src.models.enums import Role

from .exceptions import UserAlreadyActiveError, UserAlreadyInactiveError
from .value_objects import Email, PhoneNumber


@dataclass(kw_only=True)
class User(TimestampedEntity):
    """User aggregate root.

    State is mutated only through the methods below so that invariants
    (e.g. "changing the email un-verifies it") are enforced in one place.
    Use `User.register(...)` to create a new user rather than the constructor.
    """

    full_name: str
    role: Role
    email: Email
    phone_number: PhoneNumber
    password_hash: str
    is_active: bool = True
    email_verified: bool = False

    @classmethod
    def register(
        cls,
        *,
        full_name: str,
        role: Role,
        email: str,
        phone_number: str,
        password_hash: str,
    ) -> "User":
        return cls(
            full_name=full_name,
            role=role,
            email=Email(email),
            phone_number=PhoneNumber(phone_number),
            password_hash=password_hash,
        )

    def change_full_name(self, full_name: str) -> None:
        self.full_name = full_name

    def change_role(self, role: Role) -> None:
        self.role = role

    def change_email(self, email: str) -> None:
        new_email = Email(email)
        if new_email == self.email:
            return
        self.email = new_email
        self.email_verified = False

    def change_phone_number(self, phone_number: str) -> None:
        self.phone_number = PhoneNumber(phone_number)

    def set_password(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def verify_email(self) -> None:
        self.email_verified = True

    def activate(self) -> None:
        if self.is_active:
            raise UserAlreadyActiveError()
        self.is_active = True

    def deactivate(self) -> None:
        if not self.is_active:
            raise UserAlreadyInactiveError()
        self.is_active = False
