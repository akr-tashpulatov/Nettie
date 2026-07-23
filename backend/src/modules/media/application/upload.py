from typing import Protocol


class IUploadedFile(Protocol):
    """Port for a file streamed in with a request.

    Structurally satisfied by Starlette's ``UploadFile``, which lets the service
    bound the read against the size limit without importing FastAPI.
    """

    @property
    def size(self) -> int | None: ...

    @property
    def content_type(self) -> str | None: ...

    async def read(self, size: int = -1) -> bytes: ...
