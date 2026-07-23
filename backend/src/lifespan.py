from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.broker import broker
from src.core.database import check_db_connection, close_db_connection
from src.core.health import mark_app_ready
from src.core.storage import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: warm pools, ping deps
    await check_db_connection()
    await storage_service.connect()

    # Start the task broker so the API (producer) can enqueue tasks via .kiq().
    if not broker.is_worker_process:
        await broker.startup()

    # Mark app ready
    mark_app_ready()

    yield

    # shutdown: dispose engine, close clients
    if not broker.is_worker_process:
        await broker.shutdown()
    await storage_service.close()
    await close_db_connection()
