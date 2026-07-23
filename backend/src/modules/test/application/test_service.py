import math

from src.core.dtos.pagination import PaginatedResponse

from ..domain.entities import Question, Test
from ..domain.exceptions import (
    QuestionNotFoundError,
    TestNameAlreadyExistsError,
    TestNotFoundError,
)
from .dtos import (
    QuestionCreateDto,
    QuestionUpdateDto,
    TestCreateDto,
    TestsQueryDto,
    TestUpdateDto,
)
from .parsing import IQuestionParser
from .repository import IQuestionRepository, ITestRepository


class TestService:
    def __init__(
        self,
        tests: ITestRepository,
        questions: IQuestionRepository,
        parser: IQuestionParser,
    ):
        self.tests = tests
        self.questions = questions
        self.parser = parser

    async def create(self, data: TestCreateDto) -> Test:
        if await self.tests.exists_by_name(data.name):
            raise TestNameAlreadyExistsError()
        test = Test.create(name=data.name, mode=data.mode, created_by=data.created_by)
        return await self.tests.add(test)

    async def get_tests(self, query: TestsQueryDto) -> PaginatedResponse[Test]:
        tests, total = await self.tests.get_many(query)
        return PaginatedResponse[Test](
            page=query.page,
            limit=query.limit,
            items=tests,
            total_count=total,
            page_count=math.ceil(total / query.limit) if query.limit else 0,
        )

    async def get_by_id(self, test_id: int) -> Test:
        test = await self.tests.get_by_id(test_id)
        if not test:
            raise TestNotFoundError()
        return test

    async def update(self, test_id: int, data: TestUpdateDto) -> Test:
        test = await self.get_by_id(test_id)
        if data.name is not None:
            if await self.tests.exists_by_name(data.name, exclude_id=test_id):
                raise TestNameAlreadyExistsError()
            test.rename(data.name)
        if data.mode is not None:
            test.change_mode(data.mode)
        return await self.tests.update(test)

    async def delete(self, test_id: int) -> None:
        await self.get_by_id(test_id)
        await self.tests.delete(test_id)

    async def import_questions(self, test_id: int, content: bytes) -> int:
        await self.get_by_id(test_id)
        parsed = self.parser.parse(content)
        start = await self.questions.count_by_test(test_id)
        questions = [
            Question.create(
                test_id=test_id,
                text=item.text,
                position=start + offset,
                options=[(o.text, o.is_correct) for o in item.options],
            )
            for offset, item in enumerate(parsed)
        ]
        return await self.questions.add_many(questions)

    async def list_questions(self, test_id: int) -> list[Question]:
        await self.get_by_id(test_id)
        return await self.questions.get_by_test(test_id)

    async def add_question(self, test_id: int, data: QuestionCreateDto) -> Question:
        await self.get_by_id(test_id)
        position = await self.questions.count_by_test(test_id)
        question = Question.create(
            test_id=test_id,
            text=data.text,
            position=position,
            options=[(o.text, o.is_correct) for o in data.options],
        )
        return await self.questions.add(question)

    async def update_question(
        self, test_id: int, question_id: int, data: QuestionUpdateDto
    ) -> Question:
        question = await self._get_question(test_id, question_id)
        question.edit(
            text=data.text,
            options=[(o.text, o.is_correct) for o in data.options],
        )
        return await self.questions.update(question)

    async def delete_question(self, test_id: int, question_id: int) -> None:
        await self._get_question(test_id, question_id)
        await self.questions.delete(question_id)

    async def _get_question(self, test_id: int, question_id: int) -> Question:
        question = await self.questions.get_by_id(question_id)
        if not question or question.test_id != test_id:
            raise QuestionNotFoundError()
        return question
