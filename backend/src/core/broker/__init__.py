from taskiq import TaskiqEvents, TaskiqState
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from src.core.config import settings
from src.core.storage import storage_service

_BROKER_DB = 2
_RESULT_DB = 3

result_backend: RedisAsyncResultBackend = RedisAsyncResultBackend(
    redis_url=settings.REDIS_URL(_RESULT_DB),
)

broker = RedisStreamBroker(
    url=settings.REDIS_URL(_BROKER_DB),
).with_result_backend(result_backend)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def _connect_shared_clients(state: TaskiqState) -> None:
    await storage_service.connect()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def _close_shared_clients(state: TaskiqState) -> None:
    await storage_service.close()
