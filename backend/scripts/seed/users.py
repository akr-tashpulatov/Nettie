"""Seed application users (admins and students)."""

from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_hash
from src.models import UserModel
from src.models.enums import Role

from ._runner import run

ADMIN_PASSWORD = "Admin_992_#"
STUDENT_PASSWORD = "Student_911_#"


class SeedUser(TypedDict):
    full_name: str
    email: str
    phone_number: str
    role: Role
    password: str


USERS: list[SeedUser] = [
    {
        "full_name": "Admin",
        "email": "admin@example.com",
        "phone_number": "+77010000001",
        "role": Role.ADMIN,
        "password": ADMIN_PASSWORD,
    },
    {
        "full_name": "Student",
        "email": "student@example.com",
        "phone_number": "+77010000002",
        "role": Role.STUDENT,
        "password": STUDENT_PASSWORD,
    },
]


async def seed(session: AsyncSession) -> None:
    existing = set((await session.scalars(select(UserModel.email))).all())
    for data in USERS:
        if data["email"] in existing:
            print(f"  user exists: {data['email']}")
            continue
        session.add(
            UserModel(
                full_name=data["full_name"],
                email=data["email"],
                phone_number=data["phone_number"],
                role=data["role"],
                password_hash=get_hash(data["password"]),
                email_verified=True,
                is_active=True,
            )
        )
        print(f"  created user: {data['email']}")


if __name__ == "__main__":
    print("Seeding users...")
    run(seed)
    print("Done.")
