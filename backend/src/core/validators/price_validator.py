from decimal import Decimal
from typing import Annotated

from pydantic import Field, PlainSerializer

# A monetary amount that matches the DB column NUMERIC(12, 2): non-negative,
# at most 12 significant digits, exactly 2 decimal places. Serialized to a
# fixed 2-decimal string in JSON so the frontend always gets e.g. "100.00".
Price = Annotated[
    Decimal,
    Field(max_digits=12, decimal_places=2, ge=0, examples=["100.00", "79.99"]),
    PlainSerializer(lambda v: f"{v:.2f}", return_type=str, when_used="json"),
]
