"""ORM models. Importing them here ensures Alembic autogenerate sees every
table via `Base.metadata`."""

from app.models.base import Base
from app.models.device import Device
from app.models.entitlement import Entitlement
from app.models.photo import Photo
from app.models.plant import Plant
from app.models.preset import Preset
from app.models.species import Species
from app.models.subscription import Subscription
from app.models.usage_counter import UsageCounter
from app.models.user import User
from app.models.watering_event import WateringEvent

__all__ = [
    "Base",
    "Device",
    "Entitlement",
    "Photo",
    "Plant",
    "Preset",
    "Species",
    "Subscription",
    "UsageCounter",
    "User",
    "WateringEvent",
]
