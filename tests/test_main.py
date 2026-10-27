import httpx
from app import main

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "prism-api"
    }


def test_repository_not_found(monkeypatch):

    def fake_fetch_repository(owner, repo):
        return httpx.Response(status_code=404)

    monkeypatch.setattr(
        main,
        "fetch_repository",
        fake_fetch_repository
    )

    response = client.get("/repos/example/missing")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Repository not found."
    }

