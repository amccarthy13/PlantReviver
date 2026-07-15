from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# TODO (step 2), see ARCHITECTURE.md §6:
#   POST   /auth/apple     -> verify Apple identity token, upsert user, issue JWTs
#   POST   /auth/refresh   -> rotate access token
#   DELETE /auth/account   -> soft-delete (Apple requirement)
