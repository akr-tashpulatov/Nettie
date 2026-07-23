from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_healthz import (
    HealthCheckDatabase,
    HealthCheckRedis,
    HealthCheckRegistry,
    HealthCheckS3,
    health_check_route,
)

from src.core.config import settings

_app_ready = False


def mark_app_ready():
    global _app_ready
    _app_ready = True


async def startup_check():
    if not _app_ready:
        return JSONResponse(status_code=503, content={"status": "starting"})
    return JSONResponse(status_code=200, content={"status": "healthy"})


def setup(app: FastAPI):
    db_check = HealthCheckRegistry()
    s3_check = HealthCheckRegistry()
    redis_check = HealthCheckRegistry()
    db_check.add(HealthCheckDatabase(uri=settings.DATABASE_URL_SYNC))
    s3_check.add(
        HealthCheckS3(
            ssl=settings.AWS_S3_SECURE,
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    )
    redis_check.add(HealthCheckRedis(uri=settings.REDIS_URL()))

    app.add_api_route(
        "/health/db",
        tags=["Health"],
        endpoint=health_check_route(registry=db_check),
    )
    app.add_api_route(
        "/health/s3",
        tags=["Health"],
        endpoint=health_check_route(registry=s3_check),
    )
    app.add_api_route(
        "/health/redis",
        tags=["Health"],
        endpoint=health_check_route(registry=redis_check),
    )
    app.add_api_route("/health/application", tags=["Health"], endpoint=startup_check)
