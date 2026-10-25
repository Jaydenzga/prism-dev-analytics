
import httpx
from fastapi import FastAPI, HTTPException
from app.github_client import fetch_repository

app = FastAPI(
    title="PRISM API",
    description="Developer intelligence and repository analytics",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "prism-api"
    }


@app.get("/repos/{owner}/{repo}")
def get_repository(owner: str, repo: str):
    try:
        response = fetch_repository(owner, repo)
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not contact GitHub."
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Repository not found."
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="GitHub could not return repository data."
        )

    data = response.json()

    return {
        "name": data["full_name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "url": data["html_url"]
    }
