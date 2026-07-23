from dataclasses import dataclass

from ..domain.exceptions import QuestionNotFoundError
from .catalog import IQuestionCatalog
from .explainer import IExplanationGenerator
from .explanation_cache import IExplanationCache


@dataclass(frozen=True)
class ExplanationResult:
    question_id: int
    text: str
    cached: bool


class ExplanationService:
    def __init__(
        self,
        catalog: IQuestionCatalog,
        cache: IExplanationCache,
        generator: IExplanationGenerator,
    ) -> None:
        self.catalog = catalog
        self.cache = cache
        self.generator = generator

    async def explain(self, question_id: int) -> ExplanationResult:
        cached = await self.cache.get(question_id)
        if cached is not None:
            return ExplanationResult(question_id=question_id, text=cached, cached=True)

        question = await self.catalog.get_explainable(question_id)
        if question is None:
            raise QuestionNotFoundError()

        text = await self.generator.generate(question.build_prompt())
        await self.cache.set(question_id, text)
        return ExplanationResult(question_id=question_id, text=text, cached=False)
