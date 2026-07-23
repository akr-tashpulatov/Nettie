from sqlalchemy import delete, select

from src.core.database.interfaces.repositories import SQLAlchemyAbstractRepository
from src.models import MediaModel

from ..domain.entities import Media


class MediaRepository(SQLAlchemyAbstractRepository):
    @staticmethod
    def _to_domain(m: MediaModel) -> Media:
        return Media(
            id=m.id,
            object_bucket=m.object_bucket,
            object_key=m.object_key,
            size=m.size,
            extension=m.extension,
            mimetype=m.mimetype,
            uploaded_by=m.uploaded_by,
            created_at=m.created_at,
        )

    async def add(self, media: Media) -> Media:
        model = MediaModel(
            object_bucket=media.object_bucket,
            object_key=media.object_key,
            size=media.size,
            extension=media.extension,
            mimetype=media.mimetype,
            uploaded_by=media.uploaded_by,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, media_id: int) -> Media | None:
        model = await self.session.scalar(
            select(MediaModel).where(MediaModel.id == media_id)
        )
        return self._to_domain(model) if model else None

    async def get_by_ids(self, media_ids: list[int]) -> list[Media]:
        result = await self.session.execute(
            select(MediaModel).where(MediaModel.id.in_(media_ids))
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def delete(self, media_id: int) -> None:
        await self.session.execute(delete(MediaModel).where(MediaModel.id == media_id))
