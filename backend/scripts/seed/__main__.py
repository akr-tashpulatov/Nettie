"""Run every seeder in dependency order (services → tariffs, users)."""

from sqlalchemy.ext.asyncio import AsyncSession

from . import renewal_settings, services, tariffs, users
from ._runner import run


async def seed_all(session: AsyncSession) -> None:
    print("Seeding services...")
    await services.seed(session)
    print("Seeding tariffs...")
    await tariffs.seed(session)
    print("Seeding renewal settings...")
    await renewal_settings.seed(session)
    print("Seeding users...")
    await users.seed(session)


if __name__ == "__main__":
    run(seed_all)
    print("Done.")
