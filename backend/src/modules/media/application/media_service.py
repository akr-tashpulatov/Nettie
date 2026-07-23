import asyncio
from datetime import timedelta
from uuid import uuid4

from src.core.audit import IAuditLogger, snapshot
from src.core.config import settings

from ..domain.entities import Media
from ..domain.exceptions import (
    EmptyMediaError,
    InvalidMediaTypeError,
    MediaNotFoundError,
    MediaTooLargeError,
)
from .dtos import MediaUploadDto
from .repository import IMediaRepository
from .storage import IFileStorage
from .upload import IUploadedFile

IMAGE_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
}
MAX_IMAGE_SIZE = 16 * 1024 * 1024

AUDIO_EXTENSIONS = {
    "audio/mp4": "mp4",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
}
MAX_AUDIO_SIZE = 32 * 1024 * 1024

PRESIGNED_URL_TTL = timedelta(minutes=30)


class MediaService:
    """Owns uploaded files: their bytes in the private object store and their
    metadata in the `media` table.

    Other modules reference a `Media` by id and ask this service for a
    presigned URL when they need to hand one to a client. Deciding *who* may
    receive that URL is the referencing module's job — this service knows
    nothing about what a file is attached to.
    """

    def __init__(
        self,
        repo: IMediaRepository,
        storage: IFileStorage,
        audit: IAuditLogger,
    ):
        self.repo = repo
        self.storage = storage
        self.audit = audit

    async def upload_image(self, data: MediaUploadDto) -> Media:
        return await self._upload(
            data,
            extensions=IMAGE_EXTENSIONS,
            prefix="images",
            max_size=MAX_IMAGE_SIZE,
        )

    async def upload_audio(self, data: MediaUploadDto) -> Media:
        return await self._upload(
            data,
            extensions=AUDIO_EXTENSIONS,
            prefix="audio",
            max_size=MAX_AUDIO_SIZE,
        )

    async def _upload(
        self,
        data: MediaUploadDto,
        *,
        extensions: dict[str, str],
        prefix: str,
        max_size: int,
    ) -> Media:
        mimetype = (data.file.content_type or "").split(";")[0].strip().lower()
        if mimetype not in extensions:
            raise InvalidMediaTypeError()

        content = await self._read_within_limit(data.file, max_size)

        extension = extensions[mimetype]
        bucket = settings.AWS_S3_BUCKET_NAME
        media = Media.upload(
            object_bucket=bucket,
            object_key=f"{prefix}/{uuid4().hex}.{extension}",
            size=len(content),
            extension=extension,
            mimetype=mimetype,
            uploaded_by=data.uploaded_by,
        )

        await self.storage.upload(
            media.object_bucket, media.object_key, content, media.mimetype
        )
        created = await self.repo.add(media)
        await self.audit.log(
            action="media.upload",
            entity="media",
            entity_id=str(created.id),
            after=snapshot(created),
        )
        return created

    @staticmethod
    async def _read_within_limit(file: IUploadedFile, max_size: int) -> bytes:
        if file.size is not None and file.size > max_size:
            raise MediaTooLargeError()
        content = await file.read(max_size + 1)
        if len(content) > max_size:
            raise MediaTooLargeError()
        if not content:
            raise EmptyMediaError()
        return content

    async def delete(self, media_id: int) -> None:
        """Remove a media row and the object behind it.

        No caller yet. A referencing column (e.g. `writing_tasks.image_id`) must be
        cleared first, or the foreign key will block the delete.
        """
        media = await self.get_by_id(media_id)
        await self.repo.delete(media_id)
        await self.storage.delete(media.object_bucket, media.object_key)
        await self.audit.log(
            action="media.delete",
            entity="media",
            entity_id=str(media_id),
            before=snapshot(media),
        )

    async def get_by_id(self, media_id: int) -> Media:
        media = await self.repo.get_by_id(media_id)
        if media is None:
            raise MediaNotFoundError()
        return media

    async def download(self, media: Media) -> bytes:
        """The raw bytes, for server-side consumers (e.g. sending an image to the
        LLM) that need the content rather than a URL to hand to a client."""
        return await self.storage.download(media.object_bucket, media.object_key)

    async def presign(
        self, media: Media, expiration: timedelta = PRESIGNED_URL_TTL
    ) -> str:
        return await self.storage.presigned_get_url(
            media.object_bucket, media.object_key, expiration
        )

    async def presign_many(
        self, media_ids: list[int], expiration: timedelta = PRESIGNED_URL_TTL
    ) -> dict[int, str]:
        medias = await self.repo.get_by_ids(media_ids)
        urls = await asyncio.gather(*(self.presign(m, expiration) for m in medias))
        return {m.require_id: url for m, url in zip(medias, urls)}
