from typing import Protocol

from ..domain.entities import User
from .dtos import UsersQueryDto


class IUserRepository(Protocol):
    """Port the application depends on. Implemented in the infrastructure layer.

    Living in the application layer (next to the use cases that need it) is what
    inverts the dependency: the service talks to this abstraction and never
    imports infrastructure; infrastructure conforms to it.
    """

    async def add(self, user: User) -> User: ...

    async def get_by_id(self, user_id: int) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_phone_number(self, phone_number: str) -> User | None: ...

    async def get_many(self, query: UsersQueryDto) -> tuple[list[User], int]: ...

    async def exists_by_email(
        self, email: str, exclude_id: int | None = None
    ) -> bool: ...

    async def exists_by_phone_number(
        self, phone_number: str, exclude_id: int | None = None
    ) -> bool: ...

    async def update(self, user: User) -> User: ...
