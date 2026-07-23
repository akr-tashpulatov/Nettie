import dataclasses
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

_DEFAULT_EXCLUDE = frozenset({"password_hash"})


def snapshot(
    entity: Any, *, exclude: frozenset[str] = _DEFAULT_EXCLUDE
) -> dict[str, Any]:
    """JSON-safe dict of a domain entity for an audit `before`/`after` payload."""
    if not dataclasses.is_dataclass(entity):
        raise TypeError(f"snapshot() expects a dataclass entity, got {type(entity)!r}")
    return {
        f.name: _jsonify(getattr(entity, f.name))
        for f in dataclasses.fields(entity)
        if f.name not in exclude
    }


def _jsonify(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        data = {
            f.name: _jsonify(getattr(value, f.name)) for f in dataclasses.fields(value)
        }
        # Single-field value objects (Email, Money, ...) flatten to their value.
        return data["value"] if set(data) == {"value"} else data
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_jsonify(v) for v in value]
    return value
