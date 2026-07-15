import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SyncMixin


class Photo(Base, SyncMixin):
    __tablename__ = "photos"

    plant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    thumb_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # pending -> ready once the client confirms the direct-to-R2 upload.
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
