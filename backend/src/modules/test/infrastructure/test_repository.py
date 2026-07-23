from sqlalchemy import ColumnElement, ScalarSelect, delete, func, select, update

from src.core.database.interfaces.repositories import SQLAlchemyAbstractRepository
from src.models import QuestionModel, TestModel
from src.models.enums import TestMode

from ..application.dtos import TestsQueryDto
from ..domain.entities import Test


def _question_count_expr() -> ScalarSelect[int]:
    return (
        select(func.count())
        .select_from(QuestionModel)
        .where(QuestionModel.test_id == TestModel.id)
        .scalar_subquery()
    )


class TestRepository(SQLAlchemyAbstractRepository):
    @staticmethod
    def _to_domain(m: TestModel, question_count: int = 0) -> Test:
        return Test(
            id=m.id,
            name=m.name,
            mode=TestMode(m.mode),
            created_by=m.created_by,
            question_count=question_count,
            created_at=m.created_at,
        )

    async def add(self, test: Test) -> Test:
        model = TestModel(
            name=test.name, mode=test.mode.value, created_by=test.created_by
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, test_id: int) -> Test | None:
        stmt = select(TestModel, _question_count_expr()).where(TestModel.id == test_id)
        row = (await self.session.execute(stmt)).first()
        if row is None:
            return None
        model, count = row
        return self._to_domain(model, count)

    async def get_many(self, query: TestsQueryDto) -> tuple[list[Test], int]:
        offset = (query.page - 1) * query.limit
        count_expr = _question_count_expr()

        filters: list[ColumnElement[bool]] = []
        if query.query:
            filters.append(TestModel.name.ilike(f"%{query.query}%"))
        if query.eligible_only:
            filters.append(count_expr >= TestModel.mode)

        stmt = (
            select(TestModel, count_expr)
            .where(*filters)
            .order_by(TestModel.created_at.desc())
            .limit(query.limit)
            .offset(offset)
        )
        total_stmt = select(func.count()).select_from(TestModel).where(*filters)

        total = await self.session.scalar(total_stmt) or 0
        rows = (await self.session.execute(stmt)).all()
        return [self._to_domain(m, count) for m, count in rows], total

    async def exists_by_name(self, name: str, exclude_id: int | None = None) -> bool:
        stmt = select(TestModel.id).where(TestModel.name == name)
        if exclude_id is not None:
            stmt = stmt.where(TestModel.id != exclude_id)
        return await self.session.scalar(stmt.limit(1)) is not None

    async def update(self, test: Test) -> Test:
        stmt = (
            update(TestModel)
            .where(TestModel.id == test.id)
            .values(name=test.name, mode=test.mode.value)
            .returning(TestModel)
        )
        model = (await self.session.execute(stmt)).scalar_one()
        count = await self.session.scalar(
            select(func.count())
            .select_from(QuestionModel)
            .where(QuestionModel.test_id == test.id)
        )
        return self._to_domain(model, count or 0)

    async def delete(self, test_id: int) -> None:
        await self.session.execute(delete(TestModel).where(TestModel.id == test_id))
