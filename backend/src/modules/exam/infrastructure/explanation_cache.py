import json

from src.core.config import settings
from src.core.redis import RedisService

from ..domain.explanation import EXPLANATION_PROMPT_VERSION


def _key(question_id: int) -> str:
    return f"exam:explanation:v{EXPLANATION_PROMPT_VERSION}:{question_id}"


class RedisExplanationCache:
    """Redis-backed cache of generated explanations, keyed by question id.

    Stored as JSON (``RedisService.get`` json-decodes on read) so a bare-prose
    explanation is never misread as a JSON scalar.
    """

    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    async def get(self, question_id: int) -> str | None:
        data = await self.redis.get(_key(question_id))
        if isinstance(data, dict):
            text = data.get("text")
            return text if isinstance(text, str) else None
        return None

    async def set(self, question_id: int, explanation: str) -> None:
        await self.redis.set(
            _key(question_id),
            json.dumps({"text": explanation}),
            ttl=settings.EXPLANATION_CACHE_TTL_SECONDS,
        )
