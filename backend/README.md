# PlantReviver — Backend

Async FastAPI API. See the repo root `ARCHITECTURE.md` for the full design.

## Stack
- Python 3.12, FastAPI (fully async)
- SQLAlchemy 2.0 async + `asyncpg`, connection-pooled
- Alembic migrations
- Pydantic v2 / pydantic-settings
- Managed with [uv](https://docs.astral.sh/uv/)

## Local development

```bash
# install deps (creates .venv)
uv sync

# configure environment
cp .env.example .env      # then edit as needed

# run the API (hot reload)
uv run uvicorn app.main:app --reload

# health check
curl localhost:8000/healthz
```

## Database migrations

```bash
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

## Quality gates

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

## Layout

```
app/
  main.py          FastAPI app factory (wires rate limiter + admin)
  config.py        settings (env-driven)
  db.py            async engine + pool, session dependency
  deps.py          shared dependencies (current user, entitlement gate)
  security.py      JWT + Apple identity verification
  ratelimit.py     slowapi limiter (§12)
  admin/           SQLAdmin dashboard at /admin (§12)
  models/          SQLAlchemy ORM models
  schemas/         Pydantic request/response models
  repositories/    DB access
  services/        business logic (one per bounded module)
  routers/         HTTP endpoints (thin)
  integrations/    external clients (Apple, Claude, weather, R2, APNs)
  jobs/            placeholder for future background jobs
migrations/        Alembic
tests/
```
