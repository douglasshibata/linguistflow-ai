from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

def test_chat_success(client: TestClient, monkeypatch):
    payload = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "provider": "ollama",
        "model": "llama3.2"
    }
    response = client.post("/api/llm/chat", json=payload)
    assert response.status_code == 200
    assert "content" in response.json()
    # The default mock in conftest.py returns "STUB LESSON"
    assert response.json()["content"] == "STUB LESSON"

def test_chat_invalid_provider(client: TestClient):
    payload = {
        "messages": [{"role": "user", "content": "Hi"}],
        "provider": "nonexistent"
    }
    response = client.post("/api/llm/chat", json=payload)
    assert response.status_code == 400
    assert "provider not enabled" in response.json()["error"]

def test_chat_validation_error(client: TestClient):
    payload = {
        "messages": [{"role": "invalid_role", "content": "Hi"}]
    }
    response = client.post("/api/llm/chat", json=payload)
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()["error"] == "validation failed"
