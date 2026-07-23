FROM python:3.14-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=system

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
