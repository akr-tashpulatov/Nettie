from datetime import timedelta
from typing import Protocol


class IFileStorage(Protocol):
    """Port for the object store holding the bytes behind a `Media` row.

    The store is private: `presigned_get_url` is the only way a client ever
    reads an object.
    """

    async def upload(
        self, bucket: str, key: str, data: bytes, content_type: str
    ) -> None: ...

    async def download(self, bucket: str, key: str) -> bytes: ...

    async def delete(self, bucket: str, key: str) -> None: ...

    async def presigned_get_url(
        self, bucket: str, key: str, expiration: timedelta
    ) -> str: ...
