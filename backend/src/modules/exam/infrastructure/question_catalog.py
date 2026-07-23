from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.core.database.interfaces.repositories import SQLAlchemyAbstractRepository
from src.models import OptionModel, QuestionModel, TestModel

from ..application.catalog import AnswerKey, OptionView, QuestionView


class SqlQuestionCatalog(SQLAlchemyAbstractRepository):
    async def get_mode(self, test_id: int) -> int | None:
        return await self.session.scalar(
            select(TestModel.mode).where(TestModel.id == test_id)
        )

    async def count_by_test(self, test_id: int) -> int:
        return (
            await self.session.scalar(
                select(func.count())
                .select_from(QuestionModel)
                .where(QuestionModel.test_id == test_id)
            )
            or 0
        )

    async def random_ids(self, test_id: int, n: int) -> list[int]:
        stmt = (
            select(QuestionModel.id)
            .where(QuestionModel.test_id == test_id)
            .order_by(func.random())
            .limit(n)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_answer_key(self, question_id: int) -> AnswerKey | None:
        stmt = select(OptionModel.id, OptionModel.is_correct).where(
            OptionModel.question_id == question_id
        )
        rows = (await self.session.execute(stmt)).all()
        if not rows:
            return None
        valid_ids = {option_id for option_id, _ in rows}
        correct_id = next(
            (option_id for option_id, is_correct in rows if is_correct), None
        )
        if correct_id is None:
            return None
        return AnswerKey(correct_option_id=correct_id, valid_option_ids=valid_ids)

    async def get_question_views(
        self, question_ids: list[int]
    ) -> dict[int, QuestionView]:
        if not question_ids:
            return {}
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.id.in_(question_ids))
            .options(selectinload(QuestionModel.options))
        )
        result = await self.session.scalars(stmt)
        return {
            m.id: QuestionView(
                id=m.id,
                text=m.text,
                options=[
                    OptionView(id=o.id, text=o.text, position=o.position)
                    for o in sorted(m.options, key=lambda o: o.position)
                ],
            )
            for m in result.all()
        }
