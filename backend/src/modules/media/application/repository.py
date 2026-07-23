from typing import Protocol

from ..domain.entities import Media


class IMediaRepository(Protocol):
    """Port the application depends on. Implemented in the infrastructure layer."""

    async def add(self, media: Media) -> Media: ...

    async def get_by_id(self, media_id: int) -> Media | None: ...

    async def get_by_ids(self, media_ids: list[int]) -> list[Media]: ...

    async def delete(self, media_id: int) -> None: ...
