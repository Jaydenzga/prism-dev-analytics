import httpx
import pytest
from app.github_client import GitHubClient, GitHubError


def test_path_escapes_components():
    assert GitHubClient.repo_path("google", "guava") == "/repos/google/guava"


def test_client_handles_404_and_rate_limit():
    import asyncio

    def handler(request):
        if request.url.path.endswith("/missing"):
            return httpx.Response(404, json={"message": "Not Found"})
        return httpx.Response(403, headers={"X-RateLimit-Remaining": "0"}, json={"message": "limited"})

    async def run():
        async with GitHubClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(GitHubError) as missing:
                await client.repository("foo", "missing")
            assert missing.value.status_code == 404
            with pytest.raises(GitHubError) as limited:
                await client.repository("foo", "busy")
            assert limited.value.status_code == 429

    asyncio.run(run())


def test_client_network_failure_and_upstream_error():
    import asyncio

    def failing_transport(request):
        raise httpx.ConnectError("Network unavailable", request=request)

    def server_error(request):
        return httpx.Response(503, json={"message": "Service unavailable"})

    async def run():
        async with GitHubClient(transport=httpx.MockTransport(failing_transport)) as client:
            with pytest.raises(GitHubError) as unreachable:
                await client.repository("google", "guava")
            assert unreachable.value.status_code == 502

        async with GitHubClient(transport=httpx.MockTransport(server_error)) as client:
            with pytest.raises(GitHubError) as upstream:
                await client.repository("google", "guava")
            assert upstream.value.status_code == 502

    asyncio.run(run())
