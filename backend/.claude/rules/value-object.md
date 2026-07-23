# Rule: Value Objects

Value objects live in `src/modules/<feature>/domain/value_objects.py`. A value
object has **no identity** — it is defined entirely by its value, is immutable,
and is always valid once constructed. Use one whenever a field has rules
(format, range, normalization): `Email`, `PhoneNumber`, `Money`, `Score`, …

## Do

- Model it as a `@dataclass(frozen=True)` with a single `value` field (or a few
  related fields).
- **Validate in `__post_init__`** and raise a domain `ValidationError` subclass
  (e.g. `InvalidEmailError`) on bad input — never a bare `ValueError` that leaks
  to the client. An instance that exists is, by construction, valid.
- **Normalize** to a canonical form (lowercase email, E.164 phone). Because the
  dataclass is frozen, assign via `object.__setattr__(self, "value", normalized)`.
- Reuse existing validators from `src/core/validators` where they fit
  (`validate_kz_phone`), wrapping their `ValueError` into a domain exception.
- Provide a **`from_trusted` classmethod** that skips validation, for rehydrating
  from a trusted source (the database). Repositories use this to avoid paying
  validation cost on every read.
- Keep it framework-free (no Pydantic, no SQLAlchemy) and give it a `__str__`
  returning the underlying value.

## Don't

- Don't make it mutable or give it an `id`. Two value objects with equal values
  are equal (frozen dataclass gives you `__eq__`/`__hash__` for free).
- Don't let an invalid instance exist — no "validate later" flag.
- Don't import framework/validation libraries into the domain.

## Reference

```python
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmailError(f"Invalid email address: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    @classmethod
    def from_trusted(cls, value: str) -> "Email":
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", value)
        return obj

    def __str__(self) -> str:
        return self.value
```
