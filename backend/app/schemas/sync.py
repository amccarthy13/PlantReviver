from datetime import datetime

from pydantic import BaseModel

from app.schemas.plant import PlantCreate, PlantRead


class ChangesResponse(BaseModel):
    """Incremental pull payload for GET /sync/changes (ARCHITECTURE.md §11).

    Includes tombstoned rows so deletions propagate; `cursor` is the new
    high-water mark the client stores for the next pull.
    """

    cursor: datetime
    plants: list[PlantRead] = []
    # TODO (step 4): watering_events, presets, photos.


class PushRequest(BaseModel):
    """Batched client mutations for POST /sync/push; applied idempotently."""

    plants: list[PlantCreate] = []
    # TODO (step 4): other syncable entities + delete markers.


class PushResult(BaseModel):
    cursor: datetime
    applied: int = 0
