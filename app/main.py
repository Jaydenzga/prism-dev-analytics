"""PRISM REST API. GitHub access and calculations live in separate modules."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.analytics import build_overview
from app.github_client import GitHubClient, GitHubError
from app.storage import (
    init_db, save_snapshot, latest_snapshot, history, recent_repositories, is_fresh,
)

OWNER_PATTERN = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$"
REPO_PATTERN = r"^[a-zA-Z0-9_.-]{1,100}$"

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="PRISM API",
    description="Pull Request Insights & Software Metrics",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def validate_name(owner: str, repo: str) -> None:
    if not re.fullmatch(OWNER_PATTERN, owner) or not re.fullmatch(REPO_PATTERN, repo) or repo in (".", ".."):
        raise HTTPException(status_code=422, detail="Invalid GitHub owner or repository name.")


async def fetch_live_overview(owner: str, repo: str) -> dict:
    async with GitHubClient() as github:
        repository, pulls, commits = await github.snapshot_inputs(owner, repo)
    return build_overview(repository, pulls, commits)


@app.get("/health")
def health():
    return {"status": "ok", "service": "prism-api"}


@app.get("/repos/{owner}/{repo}")
async def get_repository(owner: str, repo: str):
    """Backward-compatible endpoint from PRISM's first lessons."""
    validate_name(owner, repo)
    try:
        async with GitHubClient() as github:
            data = await github.repository(owner, repo)
    except GitHubError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return {
        "name": data["full_name"],
        "description": data.get("description"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "url": data["html_url"],
    }


@app.get("/api/repositories/recent")
def list_recent():
    return {"repositories": recent_repositories()}


@app.get("/api/repositories/{owner}/{repo}/overview")
async def get_overview(owner: str, repo: str, refresh: bool = Query(default=False)):
    validate_name(owner, repo)
    full_name = f"{owner}/{repo}"
    cached = latest_snapshot(full_name)
    if cached and not refresh and is_fresh(cached):
        return {**cached, "source": "cache"}
    try:
        payload = await fetch_live_overview(owner, repo)
    except GitHubError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    save_snapshot(payload["repository"]["full_name"], payload)
    return payload


@app.get("/api/repositories/{owner}/{repo}/history")
def get_history(owner: str, repo: str):
    validate_name(owner, repo)
    return {"snapshots": history(f"{owner}/{repo}")}


# The built dashboard is included in the Docker image. In local Vite development,
# React uses localhost:5173 and proxies /api calls to the FastAPI backend.
DIST = Path(__file__).resolve().parent.parent / "web" / "dist"
if (DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(DIST / "assets")), name="assets")


@app.get("/", include_in_schema=False)
def root():
    if (DIST / "index.html").is_file():
        return FileResponse(DIST / "index.html")
    return {"message": "PRISM API running. Start the React frontend with npm run dev in web/, or build it with npm run build.", "docs": "/docs"}
