from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import api_v1
from src.core.config import settings
from src.core.exceptions import setup_exception_handlers
from src.core.health import setup_healthcheck
from src.core.instrumentator import setup_instrumentator
from src.core.security import setup_rate_limiter
from src.lifespan import lifespan

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

setup_healthcheck(app)
setup_rate_limiter(app)
setup_instrumentator(app)
setup_exception_handlers(app)

app.include_router(api_v1, prefix="/api")
