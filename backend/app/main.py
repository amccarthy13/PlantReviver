from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.admin.setup import mount_admin
from app.ratelimit import limiter
from app.routers import auth, health, plants, sync


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup / shutdown hooks go here (e.g. warm caches later).
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="PlantReviver API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Rate limiting (ARCHITECTURE.md §12). Default limits apply to every route
    # via the middleware; per-route overrides use @limiter.limit(...).
    app.state.limiter = limiter
    # slowapi's handler is typed for RateLimitExceeded, not the base Exception
    # signature Starlette annotates — safe to ignore.
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(plants.router)
    app.include_router(sync.router)

    # Admin dashboard at /admin (SQLAdmin).
    mount_admin(app)

    return app


app = create_app()
