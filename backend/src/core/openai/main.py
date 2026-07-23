from openai import AsyncOpenAI

from src.core.config import settings

# One pooled async client for the whole app (mirrors the redis/storage
# singletons). Construction makes no network call; an absent API key surfaces
# only when a request is made, where it is handled as an unavailable upstream.
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "")
