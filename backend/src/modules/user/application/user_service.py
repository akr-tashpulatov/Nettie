import math

from src.core.audit import IAuditLogger, snapshot
from src.core.dtos.pagination import PaginatedResponse
from src.models.enums import Role

from ..domain.entities import User
from ..domain.exceptions import (
    EmailAlreadyExistsError,
    EmailChangeNotAllowedError,
    InvalidCurrentPasswordError,
    PasswordUnchangedError,
    PhoneNumberAlreadyExistsError,
    UserNotFoundError,
)
from .dtos import MeUpdateDto, UserCreateDto, UsersQueryDto, UserUpdateDto
from .repository import IUserRepository
from .security import PasswordHasher
from .sessions import ISessionRevoker


class UserService:
    def __init__(
        self,
        repo: IUserRepository,
        hasher: PasswordHasher,
        audit: IAuditLogger,
        sessions: ISessionRevoker,
    ):
        self.repo = repo
        self.audit = audit
        self.hasher = hasher
        self.sessions = sessions

    async def create(self, data: UserCreateDto) -> User:
        if await self.repo.exists_by_email(data.email):
            raise EmailAlreadyExistsError()
        if await self.repo.exists_by_phone_number(data.phone_number):
            raise PhoneNumberAlreadyExistsError()

        user = User.register(
            full_name=data.full_name,
            role=data.role,
            email=data.email,
            phone_number=data.phone_number,
            password_hash=self.hasher.hash(data.password),
        )
        created = await self.repo.add(user)
        await self.audit.log(
            action="user.create",
            entity="user",
            entity_id=str(created.id),
            after=snapshot(created),
        )
        return created

    async def get_users(self, query: UsersQueryDto) -> PaginatedResponse[User]:
        users, total = await self.repo.get_many(query)
        return PaginatedResponse[User](
            page=query.page,
            limit=query.limit,
            items=users,
            total_count=total,
            page_count=math.ceil(total / query.limit) if query.limit else 0,
        )

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_by_email(self, email: str) -> User:
        user = await self.repo.get_by_email(email)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_by_phone_number(self, phone_number: str) -> User:
        user = await self.repo.get_by_phone_number(phone_number)
        if not user:
            raise UserNotFoundError()
        return user

    async def update_by_id(self, user_id: int, data: UserUpdateDto) -> User:
        user = await self.get_by_id(user_id)
        before = snapshot(user)

        if data.email is not None:
            if await self.repo.exists_by_email(data.email, exclude_id=user_id):
                raise EmailAlreadyExistsError()
            user.change_email(data.email)

        if data.phone_number is not None:
            if await self.repo.exists_by_phone_number(
                data.phone_number, exclude_id=user_id
            ):
                raise PhoneNumberAlreadyExistsError()
            user.change_phone_number(data.phone_number)

        if data.full_name is not None:
            user.change_full_name(data.full_name)
        if data.role is not None:
            user.change_role(data.role)
        if data.password is not None:
            user.set_password(self.hasher.hash(data.password))

        updated = await self.repo.update(user)
        await self.audit.log(
            action="user.update",
            entity="user",
            entity_id=str(user_id),
            before=before,
            after=snapshot(updated),
        )
        return updated

    async def update_me(
        self, user_id: int, actor_role: Role, data: MeUpdateDto
    ) -> User:
        user = await self.get_by_id(user_id)
        # The audit trail exists to record administrator actions, so a student
        # editing their own profile is not snapshotted or logged.
        is_admin = actor_role is Role.ADMIN
        before = snapshot(user) if is_admin else None

        if data.email is not None:
            if not is_admin:
                raise EmailChangeNotAllowedError()
            if await self.repo.exists_by_email(data.email, exclude_id=user_id):
                raise EmailAlreadyExistsError()
            user.change_email(data.email)
            # An admin edits their own address knowingly, so keep it verified:
            # change_email() un-verifies, and sign_in refuses unverified accounts.
            user.verify_email()

        if data.phone_number is not None:
            if await self.repo.exists_by_phone_number(
                data.phone_number, exclude_id=user_id
            ):
                raise PhoneNumberAlreadyExistsError()
            user.change_phone_number(data.phone_number)

        if data.full_name is not None:
            user.change_full_name(data.full_name)

        if data.new_password is not None:
            if data.old_password is None or not self.hasher.verify(
                data.old_password, user.password_hash
            ):
                raise InvalidCurrentPasswordError()
            if data.new_password == data.old_password:
                raise PasswordUnchangedError()
            user.set_password(self.hasher.hash(data.new_password))

        updated = await self.repo.update(user)
        if data.new_password is not None:
            await self.sessions.revoke_all(user_id)  # force re-login everywhere

        if is_admin:
            await self.audit.log(
                action="user.update_me",
                entity="user",
                entity_id=str(user_id),
                before=before,
                after=snapshot(updated),
            )
        return updated

    async def activate(self, user_id: int) -> User:
        user = await self.get_by_id(user_id)
        before = snapshot(user)
        user.activate()
        updated = await self.repo.update(user)
        await self.audit.log(
            action="user.activate",
            entity="user",
            entity_id=str(user_id),
            before=before,
            after=snapshot(updated),
        )
        return updated

    async def deactivate(self, user_id: int) -> User:
        user = await self.get_by_id(user_id)
        before = snapshot(user)
        user.deactivate()
        updated = await self.repo.update(user)
        await self.audit.log(
            action="user.deactivate",
            entity="user",
            entity_id=str(user_id),
            before=before,
            after=snapshot(updated),
        )
        return updated
