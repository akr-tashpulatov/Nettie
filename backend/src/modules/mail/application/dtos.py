from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, HttpUrl


class VerifyAccountMailDto(BaseModel):
    code: int
    email: EmailStr


class PasswordResetMailDto(BaseModel):
    reset_link: HttpUrl


class SubscriptionSuccessMailDto(BaseModel):
    full_name: str
    amount: Decimal
    currency: str
    valid_until: datetime
