from typing import Protocol

from ..domain.explanation import ExplanationPrompt


class IExplanationGenerator(Protocol):
    """Port over the LLM that turns a prompt into an explanation.

    Implemented in `exam/infrastructure` against a concrete provider (OpenAI).
    Raises `ExplanationUnavailableError` when the provider fails.
    """

    async def generate(self, prompt: ExplanationPrompt) -> str: ...
