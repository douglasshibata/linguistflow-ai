"""FastAPI application factory.

Wires up lifespan-managed resources (Mongo, Neo4j, Whisper, LLM router),
security middlewares (CORS, headers, rate limiting), and routers.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings, get_settings
from app.db.mongo import MongoStore
from app.db.neo4j import Neo4jStore
from app.lessons.routes import router as lessons_router
from app.chat.routes import router as chat_router
from app.llm.routes import router as llm_routes
from app.llm.router import LlmRouter
from app.logging_config import configure as configure_logging
from app.security.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.security.headers import SecureHeadersMiddleware
from app.security.rate_limit import build_limiter, rate_limit_handler
from app.speech.routes import router as speech_router
from app.speech.service import load_whisper

logger = structlog.get_logger("linguistflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    configure_logging(settings.log_level, settings.is_production())

    logger.info("startup.begin", env=settings.app_env)

    app.state.mongo = MongoStore(settings.mongo_uri, settings.mongo_database)
    try:
        await app.state.mongo.ping()
        logger.info("mongo.connected")
    except Exception as exc:  # noqa: BLE001
        logger.warning("mongo.unreachable", error=str(exc))

    app.state.neo4j = Neo4jStore(
        settings.neo4j_uri,
        settings.neo4j_user,
        settings.neo4j_password.get_secret_value(),
    )
    try:
        await app.state.neo4j.verify_connectivity()
        logger.info("neo4j.connected")
    except Exception as exc:  # noqa: BLE001
        logger.warning("neo4j.unreachable", error=str(exc))

    logger.info("whisper.loading", model=settings.whisper_model)
    app.state.whisper = load_whisper(settings.whisper_model)
    logger.info("whisper.loaded")

    app.state.llm = LlmRouter(settings)
    logger.info(
        "llm.ready",
        default=app.state.llm.default_provider,
        providers=list(app.state.llm.list_providers().keys()),
    )

    yield

    logger.info("shutdown.begin")
    try:
        await app.state.neo4j.close()
    except Exception:  # noqa: BLE001
        pass
    try:
        app.state.mongo.close()
    except Exception:  # noqa: BLE001
        pass
    logger.info("shutdown.complete")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    limiter = build_limiter(settings)

    app = FastAPI(
        title="LinguistFlow AI",
        version="2.0.0",
        lifespan=lifespan,
        docs_url=None if settings.is_production() else "/docs",
        redoc_url=None,
        openapi_url=None if settings.is_production() else "/openapi.json",
    )
    app.state.settings = settings
    app.state.limiter = limiter

    # Middlewares are applied in reverse order — last added runs first.
    app.add_middleware(SecureHeadersMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    # In development, allow all origins for easier integration with Streamlit iframes
    cors_origins = ["*"] if not settings.is_production() else settings.cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "Authorization"],
        allow_credentials=False,
        max_age=3600,
    )

    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(lessons_router)
    app.include_router(chat_router)
    app.include_router(llm_routes)
    app.include_router(speech_router)

    @app.get("/healthz", tags=["meta"])
    async def healthz():
        return {"status": "ok", "version": app.version}

    @app.get("/readyz", tags=["meta"])
    async def readyz():
        return {
            "status": "ready",
            "providers": list(app.state.llm.list_providers().keys()),
            "default_provider": app.state.llm.default_provider,
        }

    return app


app = create_app()
