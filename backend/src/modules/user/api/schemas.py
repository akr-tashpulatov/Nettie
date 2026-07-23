from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator

from src.core.dtos import PaginatedResponse, PaginationParams
from src.core.validators import Password, PhoneNumber
from src.models.enums import Role

from ..domain.entities import User


class UserCreate(BaseModel):
    full_name: str
    role: Role
    email: EmailStr
    phone_number: PhoneNumber
    password: Password


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
    password: Optional[Password] = None


class MeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None
    old_password: Optional[str] = None
    new_password: Optional[Password] = None

    @model_validator(mode="after")
    def _passwords_together(self) -> "MeUpdate":
        if (self.old_password is None) != (self.new_password is None):
            raise ValueError("old_password and new_password must be sent together")
        return self


class MeResponse(BaseModel):
    id: int
    full_name: str
    role: Role
    email: EmailStr
    phone_number: PhoneNumber

    @classmethod
    def from_entity(cls, user: User) -> "MeResponse":
        return cls(
            id=user.require_id,
            full_name=user.full_name,
            role=user.role,
            email=user.email.value,
            phone_number=user.phone_number.value,
        )


class UserResponse(BaseModel):
    id: int
    full_name: str
    role: Role
    email: EmailStr
    phone_number: PhoneNumber
    is_active: bool
    email_verified: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.require_id,
            full_name=user.full_name,
            role=user.role,
            email=user.email.value,
            phone_number=user.phone_number.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.require_created_at,
        )


class UsersList(PaginatedResponse[UserResponse]):
    @classmethod
    def from_domain(cls, page: PaginatedResponse[User]) -> "UsersList":
        return cls(
            page=page.page,
            limit=page.limit,
            items=[UserResponse.from_entity(u) for u in page.items],
            page_count=page.page_count,
            total_count=page.total_count,
        )


class UsersQuery(PaginationParams):
    query: Optional[str] = None
    is_active: Optional[bool] = None
