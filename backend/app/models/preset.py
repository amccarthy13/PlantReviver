import uuid

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SyncMixin


class Preset(Base, SyncMixin):
    """Per-user watering presets (7/10/14/30 defaults + custom). Owned by
    PlantService (ARCHITECTURE.md §4)."""

    __tablename__ = "presets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
