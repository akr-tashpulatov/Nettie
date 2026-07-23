from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

ph = PasswordHasher()


def get_hash(password: str | bytes) -> str:
    return ph.hash(password)


def verify_hash(password: str | bytes, hash: str | bytes) -> bool:
    try:
        return ph.verify(hash, password)
    except Argon2Error:
        return False
