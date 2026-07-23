from dataclasses import dataclass

from .upload import IUploadedFile


@dataclass(frozen=True)
class MediaUploadDto:
    file: IUploadedFile
    uploaded_by: int
