import re
from typing import Annotated

from pydantic import AfterValidator, Field

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
_PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$")


def validate_password_complexity(v: str) -> str:
    if not _PASSWORD_PATTERN.match(v):
        raise ValueError(
            "Password must contain at least one lowercase letter, "
            "one uppercase letter, one digit, and one special character"
        )
    return v


type Password = Annotated[
    str,
    Field(
        examples=["Tech@tech722"],
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    ),
    AfterValidator(validate_password_complexity),
]
