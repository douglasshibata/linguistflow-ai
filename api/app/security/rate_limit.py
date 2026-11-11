"""SlowAPI-based rate limiting with X-Forwarded-For awareness."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.config import Settings


def _client_key(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def build_limiter(settings: Settings) -> Limiter:
    return Limiter(
        key_func=_client_key,
        default_limits=[settings.rate_limit],
        headers_enabled=True,
        storage_uri="memory://",
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"error": "rate limit exceeded", "detail": str(exc.detail)},
        headers={"Retry-After": "60"},
    )
