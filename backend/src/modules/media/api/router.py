from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.core.exceptions import error_responses
from src.modules.auth.api.guards import AdminUser, StudentUser

from ..application.dtos import MediaUploadDto
from ..application.media_service import MediaService
from ..domain.exceptions import (
    EmptyMediaError,
    InvalidMediaTypeError,
    MediaTooLargeError,
)
from .dependencies import get_media_service
from .schemas import MediaResponse

router = APIRouter(prefix="/media", tags=["Media"])


@router.post(
    "/images",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an image",
    description="Stores an image in private object storage and returns its media "
    "id along with a short-lived presigned URL. Pass the id as `image_id` when "
    "creating or updating a writing task. Accepts PNG, JPEG and WebP up to 16 MB.",
    responses=error_responses(
        InvalidMediaTypeError, MediaTooLargeError, EmptyMediaError
    ),
)
async def upload_image(
    file: Annotated[UploadFile, File()],
    service: Annotated[MediaService, Depends(get_media_service)],
    admin: AdminUser,
) -> MediaResponse:
    media = await service.upload_image(MediaUploadDto(file=file, uploaded_by=admin.sub))
    return MediaResponse.from_entity(media, url=await service.presign(media))


@router.post(
    "/audio",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an audio recording",
    description="Stores an audio recording in private object storage and returns "
    "its media id along with a short-lived presigned URL. Pass the id when "
    "submitting a speaking answer. Accepts MP4, WebM and Ogg audio up to 32 MB.",
    responses=error_responses(
        InvalidMediaTypeError, MediaTooLargeError, EmptyMediaError
    ),
)
async def upload_audio(
    file: Annotated[UploadFile, File()],
    service: Annotated[MediaService, Depends(get_media_service)],
    student: StudentUser,
) -> MediaResponse:
    media = await service.upload_audio(
        MediaUploadDto(file=file, uploaded_by=student.sub)
    )
    return MediaResponse.from_entity(media, url=await service.presign(media))
