"""Token handling: app-issued JWTs plus Sign in with Apple verification.

See ARCHITECTURE.md §6. Apple verification is stubbed until build-order step 2.
"""

import time
from typing import Any

import jwt

from app.config import settings


def _issue(subject: str, ttl_seconds: int, token_type: str) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + ttl_seconds,
        "type": token_type,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _issue(subject, settings.access_token_ttl_seconds, "access")


def create_refresh_token(subject: str) -> str:
    return _issue(subject, settings.refresh_token_ttl_seconds, "refresh")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


async def verify_apple_identity_token(identity_token: str) -> str:
    """Verify a Sign in with Apple identity token, return the stable Apple user id.

    TODO (step 2): fetch Apple's JWKS, verify signature + `aud` (bundle id) +
    `iss` (https://appleid.apple.com), then return the `sub` claim.
    """
    raise NotImplementedError
