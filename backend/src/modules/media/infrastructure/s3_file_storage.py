from datetime import timedelta

from src.core.storage import StorageService


class S3FileStorage:
    """Implements IFileStorage on top of the shared S3 storage service."""

    def __init__(self, storage: StorageService):
        self.storage = storage

    async def upload(
        self, bucket: str, key: str, data: bytes, content_type: str
    ) -> None:
        await self.storage.upload_file(bucket, key, data, content_type)

    async def download(self, bucket: str, key: str) -> bytes:
        return await self.storage.download_file(bucket, key)

    async def delete(self, bucket: str, key: str) -> None:
        await self.storage.delete_file(bucket, key)

    async def presigned_get_url(
        self, bucket: str, key: str, expiration: timedelta
    ) -> str:
        return await self.storage.generate_presigned_url(bucket, key, expiration)
