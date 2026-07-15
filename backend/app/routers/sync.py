from fastapi import APIRouter

router = APIRouter(prefix="/sync", tags=["sync"])

# TODO (step 4), see ARCHITECTURE.md §11:
#   GET  /sync/changes?since=<cursor>  -> incremental pull (incl. tombstones)
#   POST /sync/push                    -> idempotent batch apply of client mutations
