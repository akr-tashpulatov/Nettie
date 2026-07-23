from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core.exceptions import error_responses
from src.modules.auth.api.guards import AdminUser, AuthUser

from ..application.dtos import (
    MeUpdateDto,
    UserCreateDto,
    UsersQueryDto,
    UserUpdateDto,
)
from ..application.user_service import UserService
from ..domain.exceptions import (
    EmailAlreadyExistsError,
    EmailChangeNotAllowedError,
    InvalidCurrentPasswordError,
    PasswordUnchangedError,
    PhoneNumberAlreadyExistsError,
    UserNotFoundError,
)
from .dependencies import get_user_service
from .schemas import (
    MeResponse,
    MeUpdate,
    UserCreate,
    UserResponse,
    UsersList,
    UsersQuery,
    UserUpdate,
)

router = APIRouter()

me_router = APIRouter(prefix="/users/me", tags=["Users (Me)"])
admin_router = APIRouter(prefix="/admin/users", tags=["Users (Admin)"])


@me_router.get(
    "",
    response_model=MeResponse,
    summary="Get my profile",
    description="Returns the authenticated caller's own account details.",
    responses=error_responses(UserNotFoundError),
)
async def get_me(
    claims: AuthUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> MeResponse:
    user = await service.get_by_id(claims.sub)
    return MeResponse.from_entity(user)


@me_router.patch(
    "",
    response_model=MeResponse,
    summary="Update my profile",
    description="Updates the caller's own full name and phone number. Changing "
    "the email address is restricted to administrators. Sending `old_password` "
    "together with `new_password` also changes the password, which signs the "
    "account out of every other device.",
    responses=error_responses(
        UserNotFoundError,
        EmailChangeNotAllowedError,
        EmailAlreadyExistsError,
        PhoneNumberAlreadyExistsError,
        InvalidCurrentPasswordError,
        PasswordUnchangedError,
    ),
)
async def update_me(
    payload: MeUpdate,
    claims: AuthUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> MeResponse:
    user = await service.update_me(
        claims.sub,
        claims.role,
        MeUpdateDto(**payload.model_dump(exclude_unset=True)),
    )
    return MeResponse.from_entity(user)


@admin_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
    _: AdminUser,
) -> UserResponse:
    user = await service.create(UserCreateDto(**payload.model_dump()))
    return UserResponse.from_entity(user)


@admin_router.get("", response_model=UsersList)
async def get_users(
    query: Annotated[UsersQuery, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
    _: AdminUser,
) -> UsersList:
    page = await service.get_users(UsersQueryDto(**query.model_dump()))
    return UsersList.from_domain(page)


@admin_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
    _: AdminUser,
) -> UserResponse:
    user = await service.get_by_id(user_id)
    return UserResponse.from_entity(user)


@admin_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
    _: AdminUser,
) -> UserResponse:
    user = await service.update_by_id(
        user_id, UserUpdateDto(**payload.model_dump(exclude_unset=True))
    )
    return UserResponse.from_entity(user)


@admin_router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
    _: AdminUser,
) -> UserResponse:
    user = await service.activate(user_id)
    return UserResponse.from_entity(user)


@admin_router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
    _: AdminUser,
) -> UserResponse:
    user = await service.deactivate(user_id)
    return UserResponse.from_entity(user)


router.include_router(me_router)
router.include_router(admin_router)
