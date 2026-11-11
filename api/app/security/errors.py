"""Generic exception handlers — never leak stack traces or internal paths."""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("linguistflow.errors")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail if isinstance(exc.detail, str) else "request failed"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation failed",
            "fields": [
                {"loc": ".".join(str(p) for p in e["loc"]), "msg": e["msg"]}
                for e in exc.errors()
            ],
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    logger.exception("unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal server error"},
    )
