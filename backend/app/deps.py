"""Shared FastAPI dependencies: current user and the premium entitlement gate."""

from collections.abc import Callable, Coroutine
from enum import StrEnum
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.security import decode_token

bearer = HTTPBearer(auto_error=True)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Feature(StrEnum):
    """Premium features gated by the entitlements table (ARCHITECTURE.md §7)."""

    SMART_WATERING = "smart_watering"
    AI_IDENTIFY = "ai_identify"


async def get_current_user_id(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> str:
    try:
        payload = decode_token(creds.credentials)
    except Exception as exc:  # noqa: BLE001 - any decode failure is a 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type"
        )
    return str(payload["sub"])


CurrentUserId = Annotated[str, Depends(get_current_user_id)]


def require_entitlement(
    feature: Feature,
) -> Callable[..., Coroutine[Any, Any, str]]:
    """Gate a premium endpoint on an entitlement.

    Until the paywall launches the gate defaults to granted-for-all
    (ARCHITECTURE.md §7); flipping it on is a one-line change here.
    """

    async def _dep(user_id: CurrentUserId, session: SessionDep) -> str:
        # TODO (step 7): look up `entitlements` for (user_id, feature) and 402 if inactive.
        _ = feature
        return user_id

    return _dep
