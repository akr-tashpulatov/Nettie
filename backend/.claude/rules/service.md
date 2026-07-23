# Rule: Application Services

Services live in `src/modules/<feature>/application/<feature>_service.py`. A
service implements **use cases**: it orchestrates repositories, the domain, and
other ports. It is the only place that coordinates a unit of work.

## Do

- Depend on **ports (Protocols), not implementations.** Type constructor args as
  `IUserRepository`, `PasswordHasher`, etc. — defined in the `application/` layer.
  The concrete classes are injected by `api/dependencies.py`. This keeps the
  application layer free of any `infrastructure` import.
- Accept **input DTOs** (`UserCreateDto`) from `application/dtos.py`, return
  **domain entities** (or `PaginatedResponse[Entity]`). Do not accept or return
  API schemas — those belong to the `api` layer.
- Put orchestration here; put rules on the entity. The service decides *what
  steps* happen (check uniqueness → build user → persist); the entity decides
  *whether a state change is legal*.
- Create entities via their factory (`User.register(...)`), and mutate them via
  their methods (`user.change_email(...)`). Never `setattr` an entity.
- Raise **domain exceptions** (`EmailAlreadyExistsError`, `UserNotFoundError`).
  Never raise `HTTPException` — HTTP mapping happens globally.
- For existence checks use cheap boolean repo methods (`exists_by_email`) instead
  of fetching a full entity just to test for `None`.

## Don't

- Don't import FastAPI or `HTTPException`.
- Don't import `infrastructure`, SQLAlchemy, or call `session` directly — go
  through the repository port.
- Don't build SQL, manage transactions, or commit. `get_session` commits on
  success and rolls back on error; the service just does the work.
- Don't import concrete crypto (`get_hash`); use the `PasswordHasher` port.

## Reference

```python
class UserService:
    def __init__(self, repo: IUserRepository, hasher: PasswordHasher):
        self.repo = repo
        self.hasher = hasher

    async def create(self, data: UserCreateDto) -> User:
        if await self.repo.exists_by_email(data.email):
            raise EmailAlreadyExistsError()
        if await self.repo.exists_by_phone_number(data.phone_number):
            raise PhoneNumberAlreadyExistsError()
        user = User.register(
            full_name=data.full_name, role=data.role, email=data.email,
            phone_number=data.phone_number,
            password_hash=self.hasher.hash(data.password),
        )
        return await self.repo.add(user)

    async def update_by_id(self, user_id: int, data: UserUpdateDto) -> User:
        user = await self.get_by_id(user_id)            # raises UserNotFoundError
        if data.email is not None:
            if await self.repo.exists_by_email(data.email, exclude_id=user_id):
                raise EmailAlreadyExistsError()
            user.change_email(data.email)
        if data.password is not None:
            user.set_password(self.hasher.hash(data.password))
        return await self.repo.update(user)
```
