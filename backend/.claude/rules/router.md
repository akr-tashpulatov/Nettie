# Rule: Routers

Routers live in `src/modules/<feature>/api/router.py`. A router is the **thin HTTP
boundary**: it parses the request, calls one service method, and maps the result
back to a response schema. Nothing more.

Each module exposes exactly one `router` symbol, which is included into
`src/api/v1.py` under `/api/v1`. Usually that is a single
`router = APIRouter(prefix="/<plural>", tags=[...])`.

**Role-scoped sub-routers.** When a resource is exposed to more than one audience
with materially different contracts — different response schemas, different
filters, different write permissions — split it into one sub-router per role and
compose them behind the module's `router`:

```python
router = APIRouter()

admin_router = APIRouter(prefix="/admin/study-groups", tags=["Study Groups (Admin)"])
student_router = APIRouter(prefix="/student/study-groups", tags=["Study Groups (Student)"])

# ... routes ...

router.include_router(admin_router)
router.include_router(student_router)
```

This keeps the two audiences' contracts visibly separate in Swagger (one tag
each) and makes the role a route-table fact rather than something you have to
read each handler's guard to discover. The guard still goes on every route
(`_: AdminUser` / `_: StudentUser`) — the path prefix documents the audience, it
does not enforce it.

Don't reach for this when the only difference is who may call an otherwise
identical endpoint; a single router with the right guard per route is simpler.

## Do

- Inject the service via `Depends` using the module's provider:
  `service: Annotated[UserService, Depends(get_user_service)]`.
- Convert the **request schema → DTO** before calling the service
  (`UserCreateDto(**payload.model_dump())`); for PATCH use
  `payload.model_dump(exclude_unset=True)`.
- Convert the returned **entity → response schema** with `Schema.from_entity(...)`
  (or `UsersList.from_domain(...)` for lists).
- Set explicit status codes where appropriate (`status_code=status.HTTP_201_CREATED`
  for creation) and declare `response_model`.
- Keep handlers tiny — ideally three lines: build DTO, call service, map result.
- Document every endpoint for Swagger: add `summary` (short, imperative) and
  `description` (one or two sentences, the *why*/behaviour, not a restatement of
  the path) to the `@router.<method>(...)` decorator. Don't rely on the handler's
  docstring — keep the decorator the single source of truth so all metadata for
  an endpoint lives in one place.
- Document the error responses an endpoint can produce with
  `responses=error_responses(...)` (`src.core.exceptions.error_responses`),
  passing every domain exception the service call can raise. This renders each
  exception as a named example under its mapped status code in Swagger, so
  clients see concrete error bodies instead of a generic schema.
  `error_responses` reads its example `detail` from the exception's **docstring**
  — every domain exception you reference here must have one (see `.claude/rules/service.md`'s
  exception guidance); an exception without a docstring renders an empty `detail`.

## Don't

- **No `try/except` for domain errors.** Domain exceptions are translated to HTTP
  status codes centrally by the handlers in `src/core/exceptions`. Adding a
  per-route `try/except` duplicates that and risks leaking a 500.
- **No business logic, no DB access, no `session`.** If you're tempted to add an
  `if` about business state, it belongs in the service or entity.
- Don't accept or return domain entities/DTOs directly over HTTP — always go
  through `api/schemas.py`.
- Don't raise `HTTPException` for things the domain already models as exceptions.

## Reference

```python
from src.core.exceptions import error_responses

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a user account after validating email/phone uniqueness.",
    responses=error_responses(EmailAlreadyExistsError, PhoneNumberAlreadyExistsError),
)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.create(UserCreateDto(**payload.model_dump()))
    return UserResponse.from_entity(user)

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    description="Partially updates a user's profile fields.",
    responses=error_responses(UserNotFoundError, EmailAlreadyExistsError),
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.update_by_id(
        user_id, UserUpdateDto(**payload.model_dump(exclude_unset=True)))
    return UserResponse.from_entity(user)
```

See `src/modules/auth/api/router.py` for a full module applying this consistently
— every route sets `responses=error_responses(...)` with the exceptions its
service call can raise.

When you add a new domain exception, make sure it subclasses one of the semantic
bases in `src/core/domain` so it maps to the right status automatically — no
router change needed:

| Base | Status |
|---|---|
| `BadRequestError` (and bare `DomainException`) | 400 |
| `AuthenticationError` | 401 |
| `AuthorizationError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `ValidationError` | 422 |
| `RateLimitError` | 429 |
