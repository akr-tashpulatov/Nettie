"""Seed the catalogue of services that tariffs bundle."""

from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ServiceModel

from ._runner import run


class SeedService(TypedDict):
    name: str
    code: str


SERVICES: list[SeedService] = [
    {
        "name": "Speaking sessions",
        "code": "speaking_sessions",
    },
    {
        "name": "Writing sessions",
        "code": "writing_sessions",
    },
    {
        "name": "Speech assessment",
        "code": "speech_assessment",
    },
    {
        "name": "Word translations & transcription",
        "code": "word_translations",
    },
]


async def seed(session: AsyncSession) -> None:
    existing = set((await session.scalars(select(ServiceModel.code))).all())
    for data in SERVICES:
        if data["code"] in existing:
            print(f"  service exists: {data['code']}")
            continue
        session.add(ServiceModel(name=data["name"], code=data["code"]))
        print(f"  created service: {data['code']}")


if __name__ == "__main__":
    print("Seeding services...")
    run(seed)
    print("Done.")
