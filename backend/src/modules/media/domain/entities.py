from dataclasses import dataclass

from src.core.domain import TimestampedEntity


@dataclass(kw_only=True)
class Media(TimestampedEntity):
    object_bucket: str
    object_key: str
    size: int
    extension: str
    mimetype: str
    uploaded_by: int

    @classmethod
    def upload(
        cls,
        *,
        object_bucket: str,
        object_key: str,
        size: int,
        extension: str,
        mimetype: str,
        uploaded_by: int,
    ) -> "Media":
        return cls(
            object_bucket=object_bucket,
            object_key=object_key,
            size=size,
            extension=extension,
            mimetype=mimetype,
            uploaded_by=uploaded_by,
        )

    @property
    def is_image(self) -> bool:
        return self.mimetype.startswith("image/")

    @property
    def is_audio(self) -> bool:
        return self.mimetype.startswith("audio/")
