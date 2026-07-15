import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SyncMixin


class Plant(Base, SyncMixin):
    __tablename__ = "plants"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    species_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("species.id"), nullable=True
    )
    # Chosen preset value or custom interval; null means "manual next date only".
    watering_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_watering_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_watered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
