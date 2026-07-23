from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from src.core.config import settings
from src.core.logger import logging

from ..domain.exceptions import ExplanationUnavailableError
from ..domain.explanation import ExplanationPrompt


class OpenAIExplainer:
    """OpenAI-backed implementation of `IExplanationGenerator`.

    Uses the async client's Chat Completions API. Any provider or configuration
    failure is logged and surfaced as `ExplanationUnavailableError` (→ 503) so
    the caller never sees a raw upstream error.
    """

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    async def generate(self, prompt: ExplanationPrompt) -> str:
        messages: list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content=prompt.system),
            ChatCompletionUserMessageParam(role="user", content=prompt.user),
        ]
        try:
            completion = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                timeout=settings.OPENAI_TIMEOUT_SECONDS,
            )
        except OpenAIError as exc:
            logging.error("OpenAI explanation request failed: %s", exc)
            raise ExplanationUnavailableError() from exc

        text = (completion.choices[0].message.content or "").strip()
        if not text:
            logging.error("OpenAI returned an empty explanation")
            raise ExplanationUnavailableError()
        return text
