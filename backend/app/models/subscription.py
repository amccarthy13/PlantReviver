import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Subscription(Base, TimestampMixin):
    """Source-of-truth subscription state, kept fresh by StoreKit verification
    and App Store Server Notifications (ARCHITECTURE.md §7)."""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    original_transaction_id: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    environment: Mapped[str] = mapped_column(String(20), nullable=False)  # sandbox|production
