from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload

from src.core.database.interfaces.repositories import SQLAlchemyAbstractRepository
from src.models import OptionModel, QuestionModel

from ..domain.entities import Option, Question


class QuestionRepository(SQLAlchemyAbstractRepository):
    @staticmethod
    def _to_domain(m: QuestionModel) -> Question:
        return Question(
            id=m.id,
            test_id=m.test_id,
            text=m.text,
            position=m.position,
            options=[
                Option(
                    id=o.id,
                    text=o.text,
                    is_correct=o.is_correct,
                    position=o.position,
                )
                for o in sorted(m.options, key=lambda o: o.position)
            ],
        )

    @staticmethod
    def _to_model(question: Question) -> QuestionModel:
        return QuestionModel(
            test_id=question.test_id,
            text=question.text,
            position=question.position,
            options=[
                OptionModel(text=o.text, is_correct=o.is_correct, position=o.position)
                for o in question.options
            ],
        )

    async def add(self, question: Question) -> Question:
        model = self._to_model(question)
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def add_many(self, questions: list[Question]) -> int:
        models = [self._to_model(q) for q in questions]
        self.session.add_all(models)
        await self.session.flush()
        return len(models)

    async def get_by_id(self, question_id: int) -> Question | None:
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.id == question_id)
            .options(selectinload(QuestionModel.options))
        )
        model = await self.session.scalar(stmt)
        return self._to_domain(model) if model else None

    async def get_by_test(self, test_id: int) -> list[Question]:
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.test_id == test_id)
            .order_by(QuestionModel.position)
            .options(selectinload(QuestionModel.options))
        )
        result = await self.session.scalars(stmt)
        return [self._to_domain(m) for m in result.all()]

    async def count_by_test(self, test_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(QuestionModel)
            .where(QuestionModel.test_id == test_id)
        )
        return await self.session.scalar(stmt) or 0

    async def update(self, question: Question) -> Question:
        model = await self.session.get(
            QuestionModel,
            question.id,
            options=[selectinload(QuestionModel.options)],
        )
        if model is None:
            raise ValueError(f"Question {question.id} disappeared during update")
        model.text = question.text
        model.options = [
            OptionModel(text=o.text, is_correct=o.is_correct, position=o.position)
            for o in question.options
        ]
        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, question_id: int) -> None:
        await self.session.execute(
            delete(QuestionModel).where(QuestionModel.id == question_id)
        )
