import uuid
from typing import Any

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Species(Base, TimestampMixin):
    """Server-only care library; not synced to clients as user data
    (ARCHITECTURE.md §5)."""

    __tablename__ = "species"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    common_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    default_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    care_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
