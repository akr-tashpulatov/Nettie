# Rule: Dependencies (DI)

Providers live in `src/modules/<feature>/api/dependencies.py`. This is the
**composition root** for a module: the one place where abstract ports are bound
to concrete infrastructure implementations. It's the seam that lets the rest of
the code depend on interfaces.

## Do

- Write one small `get_*` function per dependency, wired with FastAPI `Depends`.
- Build the dependency graph bottom-up: session → repository → service.
  `get_session` (from `src/core/database`) provides the `AsyncSession`.
- **Type provider return values as the port**, even though you construct the
  concrete class — this documents the contract and keeps call sites abstract:

  ```python
  def get_password_hasher() -> PasswordHasher:      # port as return type
      return Argon2PasswordHasher()                 # concrete impl
  ```

- Inject ports into the service in its constructor order. This file is the only
  place in the module allowed to import from both `application` and
  `infrastructure`.
- Keep providers trivial — construction only. No queries, no business logic.

## Don't

- Don't instantiate services or repositories anywhere else (routers, services).
  Everything is wired here and injected.
- Don't put configuration or side effects in providers; read settings from
  `src/core/config`.
- Don't create a new `AsyncSession` by hand — always depend on `get_session` so
  the request-scoped transaction (commit-on-success / rollback-on-error) is used.

## Reference

```python
def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)

def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()

def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> UserService:
    return UserService(repo, hasher)
```

To swap an implementation (e.g. a fake hasher in tests, or a different repo
backend), change it **here** — no service, router, or domain code changes.

## Shared core services

Cross-cutting services in `src/core/` (Redis, S3 storage, …) are **not** tied to
one module, so they ship their own provider next to the service in
`src/core/<service>/dependencies.py`, exported from the package `__init__`:

```python
# src/core/redis/dependencies.py
from .main import RedisService, redis_service

def get_redis_service() -> RedisService:
    return redis_service          # module-level singleton, one connection pool
```

These are stateful clients with pools/connections, so the provider returns the
**module-level singleton** (`redis_service`, `storage_service`) rather than
constructing a new instance per request.

Module providers **import and reuse** these — don't redefine a
`get_redis_service()` in a module's `api/dependencies.py`:

```python
from src.core.redis import RedisService, get_redis_service

def get_auth_store(
    redis: Annotated[RedisService, Depends(get_redis_service)],
) -> IAuthStore:
    return RedisAuthStore(redis)
```
