from datetime import datetime

from pydantic import BaseModel

from ..domain.entities import Media


class MediaResponse(BaseModel):
    id: int
    size: int
    extension: str
    mimetype: str
    url: str
    created_at: datetime

    @classmethod
    def from_entity(cls, media: Media, url: str) -> "MediaResponse":
        return cls(
            id=media.require_id,
            size=media.size,
            extension=media.extension,
            mimetype=media.mimetype,
            url=url,
            created_at=media.require_created_at,
        )
