# Rule: Schemas & DTOs

There are **two distinct contracts**, kept deliberately separate so each can
evolve independently:

- **API schemas** — `src/modules/<feature>/api/schemas.py`: the HTTP request/
  response contract. This is what clients see (and what OpenAPI documents).
- **Application DTOs** — `src/modules/<feature>/application/dtos.py`: the use-case
  input contract that services accept.

Both are Pydantic v2 `BaseModel`s. The router converts a request schema into a
DTO before calling the service. Yes, they look similar at first — that is fine;
do **not** collapse them, because the public API and the use case have different
lifecycles and audiences.

## Request schemas & DTOs (input)

- Validate at the edge: use the shared annotated types from `src/core/validators`
  (`Password`, `PhoneNumber`) and Pydantic types (`EmailStr`) instead of bare `str`.
- Make optional/update fields `Optional[...] = None`. For PATCH, the router uses
  `model_dump(exclude_unset=True)` so only provided fields are touched.
- Don't expose fields a client must not set through that route (e.g. `is_active`
  is **not** on `UserUpdate`; activation has its own endpoints).
- Query schemas extend `PaginationParams` and add filters.

## Response schemas (output)

- Never expose secrets. `UserResponse` has no `password_hash`.
- Map from a **domain entity explicitly** with a `from_entity` classmethod —
  don't rely on `model_validate(entity)`, because entities hold value objects
  (`user.email` is an `Email`, not `str`). Read `entity.email.value`.
- For lists, subclass `PaginatedResponse[ItemSchema]` and add a `from_domain`
  classmethod that maps each item via `Item.from_entity`.

## Reference

```python
class UserResponse(BaseModel):
    id: int
    full_name: str
    role: Role
    email: EmailStr
    phone_number: PhoneNumber
    is_active: bool
    email_verified: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id, full_name=user.full_name, role=user.role,
            email=user.email.value, phone_number=user.phone_number.value,
            is_active=user.is_active, email_verified=user.email_verified,
            created_at=user.created_at,
        )


class UsersList(PaginatedResponse[UserResponse]):
    @classmethod
    def from_domain(cls, page: PaginatedResponse[User]) -> "UsersList":
        return cls(page=page.page, limit=page.limit,
                   items=[UserResponse.from_entity(u) for u in page.items],
                   page_count=page.page_count, total_count=page.total_count)
```
