"""Only this module communicates with GitHub's public REST API."""
from __future__ import annotations

import asyncio
import os
from urllib.parse import quote

import httpx


class GitHubError(Exception):
    """An upstream GitHub failure expressed in PRISM HTTP terms."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None):
        token = os.getenv("GITHUB_TOKEN", "").strip()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "PRISM-Developer-Analytics/1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=httpx.Timeout(12.0),
            transport=transport,
            follow_redirects=False,
        )

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)

    async def get(self, endpoint: str, params: dict | None = None):
        try:
            response = await self._client.get(endpoint, params=params)
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            raise GitHubError(502, "Could not contact GitHub.") from exc

        if response.status_code == 404:
            raise GitHubError(404, "Repository not found or not publicly accessible.")
        if response.status_code in (401, 403, 429):
            if response.headers.get("x-ratelimit-remaining") == "0" or response.status_code == 429:
                raise GitHubError(429, "GitHub API rate limit reached. Try again later or configure a token.")
            raise GitHubError(502, "GitHub denied the request. Verify permissions and token configuration.")
        if response.status_code == 409:
            return []  # An empty Git repository has no commits yet.
        if response.status_code != 200:
            raise GitHubError(502, "GitHub could not return repository data.")
        try:
            return response.json()
        except ValueError as exc:
            raise GitHubError(502, "GitHub returned an invalid JSON response.") from exc

    @staticmethod
    def repo_path(owner: str, repo: str) -> str:
        # Host is fixed; only escaped repository name components come from users.
        return f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}"

    async def repository(self, owner: str, repo: str) -> dict:
        return await self.get(self.repo_path(owner, repo))

    async def snapshot_inputs(self, owner: str, repo: str):
        root = self.repo_path(owner, repo)
        # The GitHub APIs here return the latest page of up to 100 records each.
        # They are *samples*, NOT lifetime totals.
        repository, pulls, commits = await asyncio.gather(
            self.get(root),
            self.get(root + "/pulls", {"state": "all", "sort": "created", "direction": "desc", "per_page": 100}),
            self.get(root + "/commits", {"per_page": 100}),
        )
        return repository, pulls, commits
