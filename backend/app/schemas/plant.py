import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PlantBase(BaseModel):
    name: str
    watering_interval_days: int | None = None
    next_watering_date: date | None = None
    last_watered_at: date | None = None
    notes: str = ""


class PlantCreate(PlantBase):
    # Client-generated UUID so creates are idempotent/offline-first (§11).
    id: uuid.UUID


class PlantRead(PlantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    updated_at: datetime
    deleted_at: datetime | None = None
