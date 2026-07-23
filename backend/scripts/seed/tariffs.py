"""Seed tariffs and bundle every existing service into each of them.

Depends on services already being seeded (see ``scripts.seed.services``).
"""

from decimal import Decimal
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ServiceModel, TariffItemModel, TariffModel
from src.models.enums import DurationUnit

from ._runner import run


class SeedTariff(TypedDict):
    name: str
    code: str
    base_price: Decimal
    discount_price: Decimal | None
    duration: int
    duration_unit: DurationUnit


# Prices are in KZT (tenge). Durations use DAYS since the enum has no MONTHS:
# VIP "1 month" -> 30 days, PRO "3 months" -> 90 days.
TARIFFS: list[SeedTariff] = [
    {
        "name": "Pixels Standard",
        "code": "standard",
        "base_price": Decimal("6400"),
        "discount_price": None,
        "duration": 14,
        "duration_unit": DurationUnit.DAYS,
    },
    {
        "name": "Pixels VIP",
        "code": "vip",
        "base_price": Decimal("12000"),
        "discount_price": None,
        "duration": 30,
        "duration_unit": DurationUnit.DAYS,
    },
    {
        "name": "Pixels PRO",
        "code": "pro",
        "base_price": Decimal("32000"),
        "discount_price": Decimal("30000"),
        "duration": 90,
        "duration_unit": DurationUnit.DAYS,
    },
]


async def seed(session: AsyncSession) -> None:
    service_ids = list((await session.scalars(select(ServiceModel.id))).all())
    if not service_ids:
        print("  no services found — run `python -m scripts.seed.services` first")
        return

    existing = {t.code: t for t in (await session.scalars(select(TariffModel))).all()}
    for data in TARIFFS:
        tariff = existing.get(data["code"])
        if tariff is None:
            tariff = TariffModel(
                name=data["name"],
                code=data["code"],
                base_price=data["base_price"],
                discount_price=data["discount_price"],
                duration=data["duration"],
                duration_unit=data["duration_unit"],
            )
            session.add(tariff)
            await session.flush()
            print(f"  created tariff: {data['code']}")
        else:
            print(f"  tariff exists: {data['code']}")

        linked = set(
            (
                await session.scalars(
                    select(TariffItemModel.service_id).where(
                        TariffItemModel.tariff_id == tariff.id
                    )
                )
            ).all()
        )
        for service_id in service_ids:
            if service_id in linked:
                continue
            session.add(TariffItemModel(tariff_id=tariff.id, service_id=service_id))
            print(f"    linked service {service_id} -> tariff {data['code']}")


if __name__ == "__main__":
    print("Seeding tariffs...")
    run(seed)
    print("Done.")
