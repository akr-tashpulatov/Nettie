from src.core.security import get_hash, verify_hash


class Argon2PasswordHasher:
    """Argon2 adapter implementing the application's PasswordHasher port."""

    def hash(self, password: str) -> str:
        return get_hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return verify_hash(password, password_hash)
