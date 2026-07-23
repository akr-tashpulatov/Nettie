"""Shared helper to run a seeder in its own committed session."""

import asyncio
from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal


async def run_in_session(seeder: Callable[[AsyncSession], Awaitable[None]]) -> None:
    async with AsyncSessionLocal() as session:
        await seeder(session)
        await session.commit()


def run(seeder: Callable[[AsyncSession], Awaitable[None]]) -> None:
    asyncio.run(run_in_session(seeder))
