from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def setup(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app, tags=["Metrics"])
