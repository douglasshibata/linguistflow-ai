"""Test fixtures. Stub external dependencies (Whisper, Mongo, Neo4j, LiteLLM)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings


def _stub_settings(**overrides) -> Settings:
    base = {
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DATABASE": "test",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "test",
        "APP_ENV": "test",
        "LOG_LEVEL": "WARNING",
        "RATE_LIMIT": "1000/minute",
        "LLM_DEFAULT_PROVIDER": "ollama",
        "LLM_OLLAMA_ENABLED": "true",
        "LLM_OLLAMA_BASE_URL": "http://localhost:11434",
        "LLM_OLLAMA_MODELS": "llama3.2,mistral",
    }
    base.update(overrides)
    import os
    for k, v in base.items():
        os.environ[k] = str(v)
    return Settings()


@pytest.fixture
def app(monkeypatch) -> FastAPI:
    settings = _stub_settings()

    # Stub Whisper to skip model download
    monkeypatch.setattr("app.speech.service.load_whisper", lambda name: MagicMock())

    # Stub Mongo ping
    async def _mongo_ping(self):
        return True

    monkeypatch.setattr("app.db.mongo.MongoStore.ping", _mongo_ping)

    # Stub Neo4j connectivity
    async def _neo_verify(self):
        return True

    monkeypatch.setattr("app.db.neo4j.Neo4jStore.verify_connectivity", _neo_verify)

    async def _neo_close(self):
        return None

    monkeypatch.setattr("app.db.neo4j.Neo4jStore.close", _neo_close)

    # Stub LiteLLM
    async def _fake_acompletion(**kwargs):
        response = MagicMock()
        response.choices = [MagicMock(message=MagicMock(content="STUB LESSON"))]
        return response

    monkeypatch.setattr("app.llm.router.litellm.acompletion", _fake_acompletion)

    from app.main import create_app

    return create_app(settings=settings)


@pytest.fixture
def client(app: FastAPI):
    with TestClient(app) as c:
        yield c
