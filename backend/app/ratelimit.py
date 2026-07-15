"""Rate limiting (ARCHITECTURE.md §12).

`slowapi` with the default in-memory store at launch (single instance). Swap the
storage URI for Redis when scaling to multiple instances — no code change beyond
the `Limiter(storage_uri=...)` argument.

Per-route limits are applied later with `@limiter.limit(...)`; `default_limits`
gives every route a baseline via `SlowAPIMiddleware`.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)
