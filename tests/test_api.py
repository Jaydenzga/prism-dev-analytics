from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app import main
from app.analytics import build_overview
from app.github_client import GitHubError
from app import storage
import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PRISM_DB_PATH", str(tmp_path / "test.db"))
    with TestClient(main.app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "prism-api"}


def test_overview_caching_and_history(client, monkeypatch):
    calls = []

    async def fake_fetch(owner, repo):
        calls.append((owner, repo))
        return build_overview({
            "full_name": f"{owner}/{repo}", "stargazers_count": 123,
            "forks_count": 9, "owner": {}, "html_url": "https://github.com/test/repo",
        }, [], [], now=datetime.now(timezone.utc))

    monkeypatch.setattr(main, "fetch_live_overview", fake_fetch)
    first = client.get("/api/repositories/test/repo/overview")
    second = client.get("/api/repositories/test/repo/overview")
    assert first.status_code == 200
    assert first.json()["source"] == "live"
    assert second.json()["source"] == "cache"
    assert len(calls) == 1
    assert first.json()["repository"]["stars"] == 123
    assert client.get("/api/repositories/test/repo/history").json()["snapshots"][0]["stars"] == 123
    assert client.get("/api/repositories/recent").json()["repositories"][0]["full_name"] == "test/repo"
    assert client.get("/api/repositories/test/repo/overview?refresh=true").status_code == 200
    assert len(calls) == 2


def test_upstream_error_is_safe(client, monkeypatch):
    async def failing(*args):
        raise GitHubError(429, "GitHub API rate limit reached.")

    monkeypatch.setattr(main, "fetch_live_overview", failing)
    response = client.get("/api/repositories/test/repo/overview")
    assert response.status_code == 429
    assert "rate limit" in response.json()["detail"].lower()


def test_bad_owner_and_repo_are_rejected(client):
    response = client.get("/api/repositories/.. /repo/overview")
    assert response.status_code in (404, 422)
    response = client.get("/api/repositories/user/../overview")
    assert response.status_code in (404, 422)
    response = client.get("/api/repositories/user/repo%20invalid/overview")
    assert response.status_code == 422


def test_original_repo_endpoint_maps_github_fields(client, monkeypatch):
    class FakeGitHub:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def repository(self, owner, repo):
            return {
                "full_name": f"{owner}/{repo}",
                "description": "Test repository",
                "stargazers_count": 42,
                "forks_count": 7,
                "html_url": "https://github.com/google/guava",
            }

    monkeypatch.setattr(main, "GitHubClient", FakeGitHub)
    response = client.get("/repos/google/guava")
    assert response.status_code == 200
    assert response.json() == {
        "name": "google/guava",
        "description": "Test repository",
        "stars": 42,
        "forks": 7,
        "url": "https://github.com/google/guava",
    }


def test_original_repo_endpoint_handles_upstream_error(client, monkeypatch):
    class FailingGitHub:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def repository(self, owner, repo):
            raise GitHubError(404, "Repository not found or not publicly accessible.")

    monkeypatch.setattr(main, "GitHubClient", FailingGitHub)
    response = client.get("/repos/any/missing")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
