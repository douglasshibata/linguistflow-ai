"""Security headers middleware. Uses `secure` library + manual CSP/HSTS."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

_HSTS = "max-age=31536000; includeSubDomains"
_CSP = "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'"
_PERMISSIONS = "camera=(), microphone=(), geolocation=(), payment=()"


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        h = response.headers
        h.setdefault("Strict-Transport-Security", _HSTS)
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "no-referrer")
        h.setdefault("Content-Security-Policy", _CSP)
        h.setdefault("Permissions-Policy", _PERMISSIONS)
        h.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        h.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        # Strip server identification
        if "Server" in h:
            del h["Server"]
        return response
