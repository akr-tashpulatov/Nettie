# Rule: Domain Entities

Entities live in `src/modules/<feature>/domain/entities.py`. An entity is a
business object with identity and **behaviour** — it is the heart of the domain,
not a data bag.

## Do

- Model an entity as a `@dataclass(kw_only=True)` that subclasses
  `src.core.domain.Entity` (which supplies `id: int | None = None` and
  `require_id`), or `src.core.domain.TimestampedEntity` (adds
  `created_at: datetime | None = None` and `require_created_at`) if the
  entity also tracks its creation time. Use value objects for fields that
  have rules (`Email`, `PhoneNumber`), and primitives only for plain data.
- At a call site that only ever sees an already-persisted instance — fetched
  from a repository, or just returned by `add`/`update` (see
  `.claude/rules/repository.md`) — use `entity.require_id` /
  `entity.require_created_at` instead of a bare `assert entity.id is not None`
  / `assert entity.created_at is not None`. Same `AssertionError` if the
  invariant is ever actually violated, but centralizes the narrowing instead of
  repeating it at every call site.
- Give it a **factory classmethod** for creation (`register`, `start`, `open`,
  …) that takes primitives, builds value objects, and returns a valid instance.
  Prefer this over calling the constructor from services.
- Expose **intention-revealing methods** for every state change
  (`change_email`, `activate`, `verify_email`). The method name should describe
  the business operation, not the field being set.
- Enforce invariants inside those methods. Raise a domain exception when an
  operation is illegal (`activate()` on an already-active user → `UserAlreadyActiveError`).
- Encode side-effects of a change in the same place: e.g. changing the email
  resets `email_verified = False`.

## Don't

- **No `setattr` loops** and no bulk field assignment from a service. State
  changes go through methods so invariants live in one place.
- **No framework imports.** No FastAPI, no SQLAlchemy, no Pydantic, no crypto.
  The entity must be constructible and testable with plain Python.
- Don't put persistence concerns (ids, timestamps from the DB) into business
  logic. `id` / `created_at` are nullable until the repository fills them.
- Don't redeclare `id: int | None = None` or `created_at: datetime | None = None`
  on the entity itself — those come from `Entity` / `TimestampedEntity`. An
  exception: a read-only projection that is only ever built from an
  already-written row (e.g. `AuditLogEntry`) can declare required `id: int` /
  `created_at: datetime` fields directly instead of subclassing, since it has
  no pre-persist state to narrow.
- Don't reach out to a repository, the network, or the clock from inside an
  entity. Pass what it needs as arguments (e.g. an already-computed `password_hash`).

## Reference

```python
@dataclass(kw_only=True)
class User(TimestampedEntity):
    full_name: str
    role: Role
    email: Email
    phone_number: PhoneNumber
    password_hash: str
    is_active: bool = True
    email_verified: bool = False

    @classmethod
    def register(cls, *, full_name: str, role: Role, email: str,
                 phone_number: str, password_hash: str) -> "User":
        return cls(full_name=full_name, role=role, email=Email(email),
                   phone_number=PhoneNumber(phone_number), password_hash=password_hash)

    def change_email(self, email: str) -> None:
        new_email = Email(email)
        if new_email == self.email:
            return
        self.email = new_email
        self.email_verified = False   # invariant: a changed email is unverified

    def activate(self) -> None:
        if self.is_active:
            raise UserAlreadyActiveError()
        self.is_active = True
```

See `.claude/rules/value-object.md` for the value objects, and
`.claude/rules/service.md` for how services drive these methods.
