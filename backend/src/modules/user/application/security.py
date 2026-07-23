from typing import Protocol


class PasswordHasher(Protocol):
    """Port for hashing and verifying passwords.

    Keeps the application layer free of any concrete crypto library; the
    infrastructure layer provides the implementation.
    """

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...
