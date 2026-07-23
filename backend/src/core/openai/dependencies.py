from openai import AsyncOpenAI

from .main import openai_client


def get_openai_client() -> AsyncOpenAI:
    return openai_client
