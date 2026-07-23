from typing import Annotated

import phonenumbers
from pydantic import AfterValidator, Field


def validate_kz_phone(v: str) -> str:
    try:
        parsed = phonenumbers.parse(v, "KZ")

        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number.")

        # strictly enforces the KZ region code.
        region = phonenumbers.region_code_for_number(parsed)
        if region != "KZ":
            raise ValueError("Phone number region must be KZ.")

        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    except phonenumbers.NumberParseException:
        raise ValueError("Invalid phone number format.")


PhoneNumber = Annotated[
    str,
    AfterValidator(validate_kz_phone),
    Field(examples=["+77011234567", "+77051234567"]),
]
