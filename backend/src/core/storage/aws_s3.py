import logging
from contextlib import AsyncExitStack
from datetime import timedelta
from typing import TYPE_CHECKING

import aioboto3
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError

from src.core.config import settings

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client

logger = logging.getLogger(__name__)


class StorageService:
    """Async wrapper around an aioboto3 S3 client.

    The client is opened once via ``connect()`` (called from the app
    lifespan) and reused for every operation. The configured bucket is
    created if missing and stays **private** — objects are served to
    clients exclusively through presigned URLs.
    """

    def __init__(self) -> None:
        self._session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self._stack = AsyncExitStack()
        self._client: S3Client | None = None
        self._presign_client: S3Client | None = None

    async def connect(self) -> None:
        self._client = await self._open_client(settings.AWS_S3_ENDPOINT_URL)
        presign_endpoint = settings.AWS_S3_PRESIGN_ENDPOINT_URL
        self._presign_client = (
            self._client
            if presign_endpoint == settings.AWS_S3_ENDPOINT_URL
            else await self._open_client(presign_endpoint)
        )
        await self._ensure_bucket_exists(settings.AWS_S3_BUCKET_NAME)

    async def _open_client(self, endpoint_url: str) -> "S3Client":
        return await self._stack.enter_async_context(
            self._session.client(
                "s3",
                endpoint_url=endpoint_url,
                config=AioConfig(signature_version="s3v4"),
            )
        )

    async def close(self) -> None:
        await self._stack.aclose()
        self._client = None
        self._presign_client = None

    @staticmethod
    def _require(client: "S3Client | None") -> "S3Client":
        if client is None:
            raise RuntimeError("StorageService is not connected — call connect() first")
        return client

    @property
    def client(self) -> "S3Client":
        return self._require(self._client)

    @property
    def presign_client(self) -> "S3Client":
        return self._require(self._presign_client)

    async def _ensure_bucket_exists(self, bucket: str) -> None:
        try:
            await self.client.head_bucket(Bucket=bucket)
        except ClientError:
            try:
                await self.client.create_bucket(Bucket=bucket)
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code")
                if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                    logger.exception("Failed to create bucket %s", bucket)
                    raise

    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: bytes,
        content_type: str,
    ) -> None:
        await self.client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=data,
            ContentType=content_type,
        )

    async def download_file(self, bucket: str, object_name: str) -> bytes:
        response = await self.client.get_object(Bucket=bucket, Key=object_name)
        async with response["Body"] as stream:
            return await stream.read()

    async def delete_file(self, bucket: str, object_name: str) -> None:
        await self.client.delete_object(Bucket=bucket, Key=object_name)

    async def generate_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expiration: timedelta,
    ) -> str:
        return await self.presign_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_name},
            ExpiresIn=int(expiration.total_seconds()),
        )


storage_service = StorageService()
