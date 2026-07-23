from pydantic import BaseModel, EmailStr, HttpUrl


class VerifyAccountMailDto(BaseModel):
    code: int
    email: EmailStr


class PasswordResetMailDto(BaseModel):
    reset_link: HttpUrl
