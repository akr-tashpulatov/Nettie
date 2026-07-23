from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.storage import StorageService, get_storage_service

from ..application.media_service import MediaService
from ..application.repository import IMediaRepository
from ..application.storage import IFileStorage
from ..infrastructure.media_repository import MediaRepository
from ..infrastructure.s3_file_storage import S3FileStorage


def get_media_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IMediaRepository:
    return MediaRepository(session)


def get_file_storage(
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> IFileStorage:
    return S3FileStorage(storage)


def get_media_service(
    repo: Annotated[IMediaRepository, Depends(get_media_repository)],
    storage: Annotated[IFileStorage, Depends(get_file_storage)],
) -> MediaService:
    return MediaService(repo, storage)
