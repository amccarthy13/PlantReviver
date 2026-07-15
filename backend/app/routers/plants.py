from fastapi import APIRouter

router = APIRouter(prefix="/plants", tags=["plants"])

# TODO (step 3), see ARCHITECTURE.md §4:
#   GET/POST/PATCH/DELETE /plants          -> CRUD
#   POST /plants/{id}/water                -> record a watering event
#   GET/POST/PATCH/DELETE /plants/presets  -> watering presets
