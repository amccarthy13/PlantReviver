FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# uv provides fast, reproducible dependency installs.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install deps first for better layer caching.
COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .

EXPOSE 8000

# Render injects $PORT. Gunicorn manages Uvicorn workers for the async app.
CMD ["sh", "-c", "uv run gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} -w ${WEB_CONCURRENCY:-2}"]
