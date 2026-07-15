from app.models.plant import Plant
from app.repositories.base import BaseRepository


class PlantRepository(BaseRepository[Plant]):
    model = Plant

    # TODO (step 3/4): list_for_user, get, upsert (idempotent by id),
    # changes_since(cursor) including tombstones (ARCHITECTURE.md §11).
