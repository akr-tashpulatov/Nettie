from typing import Optional

from pydantic import BaseModel, EmailStr

from src.core.dtos.pagination import PaginationParams
from src.core.validators.password_validator import Password
from src.core.validators.phone_number_validator import PhoneNumber
from src.models.enums import Role


class UserCreateDto(BaseModel):
    full_name: str
    role: Role
    email: EmailStr
    phone_number: PhoneNumber
    password: Password


class UserUpdateDto(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
    password: Optional[Password] = None


class MeUpdateDto(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None
    old_password: Optional[str] = None
    new_password: Optional[Password] = None


class UsersQueryDto(PaginationParams):
    query: Optional[str] = None
    is_active: Optional[bool] = None
