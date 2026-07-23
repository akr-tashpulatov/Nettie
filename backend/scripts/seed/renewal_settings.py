"""Seed the singleton subscription-renewal settings row if it doesn't exist."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import RenewalSettingsModel
from src.models.enums import DurationUnit

from ._runner import run

SETTINGS_ID = 1
DEFAULT_PRICE = Decimal("5000")
DEFAULT_CURRENCY = "KZT"
DEFAULT_DURATION = 1
DEFAULT_DURATION_UNIT = DurationUnit.MONTHS


async def seed(session: AsyncSession) -> None:
    existing = await session.get(RenewalSettingsModel, SETTINGS_ID)
    if existing is not None:
        print("  renewal settings exist")
        return

    session.add(
        RenewalSettingsModel(
            id=SETTINGS_ID,
            price=DEFAULT_PRICE,
            currency=DEFAULT_CURRENCY,
            duration=DEFAULT_DURATION,
            duration_unit=DEFAULT_DURATION_UNIT,
        )
    )
    print(
        f"  created renewal settings: {DEFAULT_PRICE} {DEFAULT_CURRENCY} / "
        f"{DEFAULT_DURATION} {DEFAULT_DURATION_UNIT.value}"
    )


if __name__ == "__main__":
    print("Seeding renewal settings...")
    run(seed)
    print("Done.")
