from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

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
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(plants.router)
    app.include_router(sync.router)
    return app


app = create_app()
