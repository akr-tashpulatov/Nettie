## Project

The backend is an async Python API built with FastAPI and SQLAlchemy, organised
as a set of self-contained modules following **Domain-Driven Design (DDD)** with
a clean, layered architecture.

## Technical stack

- **Language / runtime:** Python ≥ 3.14, fully async (`async`/`await`).
- **Web framework:** FastAPI (`fastapi[standard]`).
- **ORM / DB:** SQLAlchemy 2.0 (async, `asyncpg`) on PostgreSQL; migrations via Alembic.
- **Cache / queue:** Redis (`redis[hiredis]`), background tasks via TaskIQ (`taskiq`, `taskiq-redis`).
- **Auth / security:** JWT, Argon2 password hashing (`argon2-cffi`), rate limiting via SlowAPI.
- **Validation / settings:** Pydantic v2 + `pydantic-settings`.
- **Storage:** AWS S3 (`boto3`) for audio and other assets.
- **Email:** `aiosmtplib` + Jinja2 templates.
- **Observability:** Prometheus instrumentator, structured logging, health checks.
- **Tooling:** `uv` (deps & lockfile), Ruff (lint/format), mypy (types), pre-commit.

## Architecture

The project is organised by **feature module**, and each module is split into the
classic DDD layers. The golden rule is the **dependency direction**:

```
api  →  application  →  domain  ←  infrastructure
```

- **domain** depends on nothing (pure Python + value objects + entities). No
  FastAPI, no SQLAlchemy, no crypto libraries.
- **application** orchestrates use cases. It depends on the domain and on its own
  **ports** (Protocols), never on concrete infrastructure.
- **infrastructure** implements the ports (DB repositories, hashers, S3, etc.). It
  depends inward on domain/application abstractions.
- **api** is the thin HTTP boundary: routers, request/response schemas, and DI
  wiring. It depends on application; it never touches the DB directly.

Concrete enforcement of this rule:

- The application layer **must not import** from `infrastructure`. It depends on a
  port (e.g. `application/repository.py`'s `IUserRepository`,
  `application/security.py`'s `PasswordHasher`); `api/dependencies.py` injects the
  concrete implementation.
- The domain layer **must not import** FastAPI, SQLAlchemy, or any library. Domain
  exceptions subclass the framework-free bases in `src/core/domain`.
- Mapping between layers is **explicit**: SQLAlchemy model ↔ domain entity in the
  repository; domain entity ↔ response schema in the router (`from_entity`).

## Module structure

Each feature lives under `src/modules/<feature>/` with this shape (the `user`
module is the reference implementation):

```
src/modules/user/
├── api/                      # HTTP boundary
│   ├── router.py             # FastAPI routes; thin, no business logic
│   ├── schemas.py            # Pydantic request/response models (the public contract)
│   └── dependencies.py       # DI providers wiring ports → implementations
├── application/              # use cases / orchestration
│   ├── user_service.py       # the service: coordinates repo + domain + ports
│   ├── dtos.py               # input DTOs validated at the use-case boundary
│   ├── repository.py         # IUserRepository PORT (Protocol) the service depends on
│   └── security.py           # PasswordHasher PORT (Protocol)
├── domain/                   # pure business core
│   ├── entities.py           # aggregates with behaviour (e.g. User)
│   ├── value_objects.py      # validated immutable values (Email, PhoneNumber)
│   └── exceptions.py         # domain errors (subclass core semantic bases)
└── infrastructure/           # concrete adapters implementing the ports
    ├── user_repository.py    # SQLAlchemy implementation of IUserRepository
    └── password_hasher.py    # Argon2 implementation of PasswordHasher
```

Not every module needs every file — add a layer only when there's something to put
in it. The `mail` module, for example, is application-only.

## Shared core (`src/core/`)

Cross-cutting building blocks shared by all modules:

- `config.py` — `Settings` (pydantic-settings), import the singleton `settings`.
- `domain/` — framework-free exception bases mapped to HTTP statuses by the
  global handler (see "Errors" below): `DomainException` (400),
  `BadRequestError` (400), `ValidationError` (422), `AuthenticationError` (401),
  `AuthorizationError` (403), `NotFoundError` (404), `ConflictError` (409),
  `RateLimitError` (429).
- `database/` — async engine + `get_session` (commits on success, rolls back on
  error), declarative `Base`, and `IdMixin` / `UUIDMixin` / `TimestampMixin`.
- `interfaces/` & `database/interfaces/` — `AbstractRepository` /
  `SQLAlchemyAbstractRepository` base classes.
- `dtos/pagination.py` — `PaginationParams` and generic `PaginatedResponse[T]`.
- `validators/` — reusable Pydantic annotated types (`Password`, `PhoneNumber`).
- `security/` — Argon2 `get_hash`/`verify_hash`, SlowAPI rate limiter.
- `exceptions/` — global FastAPI exception handlers (domain → HTTP status map).
- `storage/` (S3), `redis/`, `health/`, `instrumentator/`, `logger.py`, `decorators/`.
- `audit/` — `AuditActor` context var (`set_actor`/`get_actor`) for tagging who
  did what; backs `src/models/audit_log.py`.
- `broker/` — the shared TaskIQ `broker` (Redis stream + result backend) that
  background tasks register against.
- `cookie/` — `CookieService` for setting/reading HTTP-only cookies (e.g. the
  auth refresh token).

Stateful core services (`redis/`, `storage/`) expose a module-level singleton
plus a FastAPI provider in `src/core/<service>/dependencies.py`
(`get_redis_service`, `get_storage_service`). Modules import and reuse these
rather than constructing their own — see `.claude/rules/dependency.md`.

`src/models/` holds **all SQLAlchemy models** (persistence), kept separate from
domain entities. `src/main.py` builds the app; `src/api/v1.py` aggregates module
routers under `/api/v1`; `src/lifespan.py` manages startup/shutdown.

## Conventions

- **Async everywhere.** Services, repositories, and routes are `async def`.
- **Naming:** SQLAlchemy models end in `Model` (`UserModel`); domain entities are
  plain (`User`); ports are prefixed `I...` or named `...er` (`IUserRepository`,
  `PasswordHasher`); input DTOs end in `Dto`; API schemas do not.
- **DTOs vs schemas:** `application/dtos.py` are the use-case contract; `api/schemas.py`
  are the HTTP contract. They are intentionally separate so each can evolve.
- **Errors:** raise domain exceptions from application/domain; never raise
  `HTTPException` there. Every domain exception subclasses one of the semantic
  bases in `src/core/domain` (`BadRequestError`, `ValidationError`,
  `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `ConflictError`,
  `RateLimitError`); the global handler in `core/exceptions` maps each base to a
  status code, so a new exception gets the right status for free and routers stay
  free of `try/except`.
- **Don't put business logic in routers or repositories.** Routers translate
  HTTP↔use-case; repositories translate model↔entity. Logic lives in the
  service and the entity.
- **No obvious comments.** Don't restate what the code plainly says or explain a
  well-known idiom. Comments like these add noise, not signal:

  ```python
  # Set is_active to True
  user.is_active = True

  # Loop over users and add them to the list
  for user in users:
      result.append(user)
  ```

  Only comment when the *why* is genuinely non-obvious from the code and can't be
  made clear by better naming — a subtle invariant, a workaround, a non-local
  consequence. When in doubt, leave it out. For example, this comment earns its
  place because the *why* (a specific bug workaround) isn't visible in the code
  itself:

  ```python
  # asyncpg 0.31 truncates microseconds on COPY; round-trip through isoformat()
  # to preserve them until the upstream fix lands.
  ```

## How to write each layer

Detailed, enforceable rules live in `.claude/rules/` — read the relevant one
before adding or changing that kind of file:

- `.claude/rules/entity.md` — domain entities (aggregates).
- `.claude/rules/value-object.md` — value objects.
- `.claude/rules/service.md` — application services / use cases.
- `.claude/rules/repository.md` — repository ports and SQLAlchemy implementations.
- `.claude/rules/schema.md` — API request/response schemas and DTOs.
- `.claude/rules/router.md` — FastAPI routers.
- `.claude/rules/dependency.md` — DI providers.

## Commands

```bash
uv sync                       # install deps from uv.lock
uv run uvicorn src.main:app --reload   # run the API locally
uv run alembic upgrade head            # apply DB migrations
uv run alembic revision --autogenerate -m "msg"  # create a migration
uv run ruff check src                  # lint
uv run ruff format src                 # format
uv run mypy src                        # type-check
docker compose up                      # full stack (api + postgres + redis)
```
