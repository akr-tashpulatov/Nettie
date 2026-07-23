from typing import Protocol


class IExplanationCache(Protocol):
    """Port over the store that caches generated explanations by question id.

    Implemented in `exam/infrastructure` against Redis with a multi-day TTL, so
    a popular question's concept is explained by the model once, not per click.
    """

    async def get(self, question_id: int) -> str | None: ...

    async def set(self, question_id: int, explanation: str) -> None: ...
