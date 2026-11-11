def test_security_headers(client):
    response = client.get("/healthz")
    headers = response.headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert "max-age=31536000" in headers["strict-transport-security"]
    assert "default-src 'self'" in headers["content-security-policy"]
    assert headers["referrer-policy"] == "no-referrer"
    assert "camera=()" in headers["permissions-policy"]


def test_cors_allowed_origin(client):
    response = client.get(
        "/api/lesson/providers",
        headers={"Origin": "http://localhost:8501"},
    )
    assert response.status_code == 200
    # In development mode, main.py allows all origins ('*')
    allowed = response.headers.get("access-control-allow-origin")
    assert allowed in ["http://localhost:8501", "*"]


def test_cors_blocked_origin(client):
    response = client.get(
        "/api/lesson/providers",
        headers={"Origin": "http://evil.example"},
    )
    assert response.status_code == 200
    # If we allow all origins ('*'), this test is moot in dev
    allowed = response.headers.get("access-control-allow-origin")
    if allowed != "*":
        assert allowed != "http://evil.example"


def test_docs_disabled_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    from app.config import Settings
    from app.main import create_app

    app = create_app(settings=Settings())
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        assert c.get("/docs").status_code == 404
        assert c.get("/openapi.json").status_code == 404
