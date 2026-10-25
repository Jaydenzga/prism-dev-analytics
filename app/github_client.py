
import httpx

def fetch_repository(owner: str, repo: str) -> httpx.Response:
    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = httpx.get(
        url,
        headers={"Accept": "application/vnd.github+json"},
        timeout=10.0
    )

    return response
