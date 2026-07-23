# Rule: Repositories

A repository has **two parts**:

1. **The port** — `src/modules/<feature>/application/repository.py`: a `Protocol`
   (`IUserRepository`) describing what the application needs. This is the
   abstraction the service depends on.
2. **The implementation** — `src/modules/<feature>/infrastructure/<feature>_repository.py`:
   a concrete SQLAlchemy class that conforms to the port and subclasses
   `SQLAlchemyAbstractRepository` (which provides `self.session`).

Defining the port in `application/` and the implementation in `infrastructure/`
is what inverts the dependency: the service never imports infrastructure.

## Do (port)

- Express methods in **domain terms**: take/return domain **entities**, not
  models. Return `Entity | None` for single lookups and `tuple[list[Entity], int]`
  for paginated lists (items + total).
- Provide cheap `exists_by_*(value, exclude_id=None) -> bool` methods for
  uniqueness checks (`exclude_id` lets updates ignore the current row).

## Do (implementation)

- **Map model ↔ entity explicitly** with `_to_domain` (and inline construction
  for writes). Rebuild value objects with `from_trusted(...)` — DB data is already
  validated, so don't re-run validation on every row.
- Map **every** column you persist. A missing field here silently drops data
  (e.g. forgetting `email_verified`).
- `add`: build the model, `session.add`, `await session.flush()` to populate the
  PK/defaults, then return `_to_domain(model)`.
- `update`: use `update(...).where(id == entity.id).values(...).returning(Model)`
  and map the returned row back. Update by the **entity's own id**.
- Keep queries here: filtering, search (`ilike`), ordering, `limit`/`offset`.

## Don't

- **No business logic** and no domain exceptions (`UserNotFoundError` is the
  service's job — the repo returns `None`). The repo only translates
  model↔entity and talks to the session.
- Don't `commit` or `rollback` — `get_session` owns the transaction.
- Don't return SQLAlchemy models out of the repository; the rest of the app never
  sees `...Model` types.
- Don't leak `value_objects` into SQL — write `entity.email.value`, read with
  `Email.from_trusted(model.email)`.

## Reference

```python
class UserRepository(SQLAlchemyAbstractRepository):     # implements IUserRepository
    @staticmethod
    def _to_domain(m: UserModel) -> User:
        return User(
            id=m.id, email=Email.from_trusted(m.email),
            phone_number=PhoneNumber.from_trusted(m.phone_number),
            password_hash=m.password_hash, role=m.role, full_name=m.full_name,
            is_active=m.is_active, email_verified=m.email_verified,
            created_at=m.created_at,
        )

    async def add(self, user: User) -> User:
        model = UserModel(email=user.email.value, phone_number=user.phone_number.value,
                          password_hash=user.password_hash, role=user.role,
                          full_name=user.full_name, is_active=user.is_active,
                          email_verified=user.email_verified)
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def exists_by_email(self, email: str, exclude_id: int | None = None) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email)
        if exclude_id is not None:
            stmt = stmt.where(UserModel.id != exclude_id)
        return await self.session.scalar(stmt.limit(1)) is not None
```
