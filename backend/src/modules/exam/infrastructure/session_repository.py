from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from src.core.database.interfaces.repositories import SQLAlchemyAbstractRepository
from src.models import SessionItemModel, TestSessionModel

from ..application.dtos import SessionsQueryDto
from ..domain.entities import SessionItem, TestSession


class SessionRepository(SQLAlchemyAbstractRepository):
    @staticmethod
    def _to_domain(m: TestSessionModel) -> TestSession:
        return TestSession(
            id=m.id,
            test_id=m.test_id,
            student_id=m.student_id,
            status=m.status,
            total=m.total,
            correct_count=m.correct_count,
            completed_at=m.completed_at,
            created_at=m.created_at,
            items=[
                SessionItem(
                    id=i.id,
                    question_id=i.question_id,
                    position=i.position,
                    selected_option_id=i.selected_option_id,
                    is_correct=i.is_correct,
                    answered_at=i.answered_at,
                )
                for i in sorted(m.items, key=lambda i: i.position)
            ],
        )

    async def add(self, session: TestSession) -> TestSession:
        model = TestSessionModel(
            test_id=session.test_id,
            student_id=session.student_id,
            status=session.status,
            total=session.total,
            correct_count=session.correct_count,
            completed_at=session.completed_at,
            items=[
                SessionItemModel(question_id=i.question_id, position=i.position)
                for i in session.items
            ],
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, session_id: int) -> TestSession | None:
        stmt = (
            select(TestSessionModel)
            .where(TestSessionModel.id == session_id)
            .options(selectinload(TestSessionModel.items))
        )
        model = await self.session.scalar(stmt)
        return self._to_domain(model) if model else None

    async def get_many_by_student(
        self, student_id: int, query: SessionsQueryDto
    ) -> tuple[list[TestSession], int]:
        offset = (query.page - 1) * query.limit
        stmt = (
            select(TestSessionModel)
            .where(TestSessionModel.student_id == student_id)
            .order_by(TestSessionModel.created_at.desc())
            .limit(query.limit)
            .offset(offset)
            .options(selectinload(TestSessionModel.items))
        )
        total_stmt = (
            select(func.count())
            .select_from(TestSessionModel)
            .where(TestSessionModel.student_id == student_id)
        )
        total = await self.session.scalar(total_stmt) or 0
        result = await self.session.scalars(stmt)
        return [self._to_domain(m) for m in result.all()], total

    async def save_answer(self, item: SessionItem, session: TestSession) -> None:
        await self.session.execute(
            update(SessionItemModel)
            .where(SessionItemModel.id == item.id)
            .values(
                selected_option_id=item.selected_option_id,
                is_correct=item.is_correct,
                answered_at=item.answered_at,
            )
        )
        await self.session.execute(
            update(TestSessionModel)
            .where(TestSessionModel.id == session.id)
            .values(
                correct_count=session.correct_count,
                status=session.status,
                completed_at=session.completed_at,
            )
        )
