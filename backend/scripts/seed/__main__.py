"""Run every seeder in dependency order."""

from sqlalchemy.ext.asyncio import AsyncSession

from . import users
from ._runner import run


async def seed_all(session: AsyncSession) -> None:
    print("Seeding users...")
    await users.seed(session)


if __name__ == "__main__":
    run(seed_all)
    print("Done.")
