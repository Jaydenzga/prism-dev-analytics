
from fastapi.testclient import TestClient

from app import main
from app.main import app
from app.github_client import GitHubError


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "prism-api"
    }


def test_repository_not_found(monkeypatch):

    class FakeGitHubClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def repository(self, owner, repo):
            raise GitHubError(
                404,
                "Repository not found or not publicly accessible."
            )

    monkeypatch.setattr(
        main,
        "GitHubClient",
        FakeGitHubClient
    )

    response = client.get("/repos/example/missing")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Repository not found or not publicly accessible."
    }
