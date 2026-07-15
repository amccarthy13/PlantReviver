import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SyncMixin


class WateringEvent(Base, SyncMixin):
    """Append-only log of waterings. Two devices simply union their events on
    sync — no real conflict exists (ARCHITECTURE.md §11)."""

    __tablename__ = "watering_events"

    plant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    watered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
