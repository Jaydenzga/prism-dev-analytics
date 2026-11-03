# PRISM

**Pull Request Insights & Software Metrics** — a developer analytics dashboard for public GitHub repositories. Built with FastAPI, HTTPX, SQLite, React, TypeScript, and Vite.

## Features

- Analyze a public GitHub repository by `owner/repo` or GitHub URL.
- See its GitHub metadata, recent pull requests, and a 14-day chart of sampled commits.
- View sampled merge rates, approximate time-to-merge, and identified commit authors.
- Cache responses for 10 minutes and save up to 30 local snapshots per repository.
- Browse previously analyzed repositories and compare actual snapshots across refreshes.
- Run automated backend tests, a frontend typecheck/build, and GitHub Actions CI.

> **Data accuracy:** PRISM requests **at most 100 newest commits and 100 newest pull requests**, not the repository's complete history. A high-traffic repository can have more than 100 commits in 14 days. PR metrics are sample estimates, not lifetime figures. Stars and forks come from repository-wide metadata.

## Run locally

Requires Python 3.11+ and Node.js 22+.

Open terminal one, from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open terminal two:

```bash
cd web
npm install
npm run dev
```

- Dashboard: http://127.0.0.1:5173
- API documentation: http://127.0.0.1:8000/docs
- API health: http://127.0.0.1:8000/health

The dev server proxies `/api` calls to the backend.

## Optional GitHub token

You can analyze public repositories without a token, but unauthenticated GitHub API calls have stricter rate limits. To use a token, provide `GITHUB_TOKEN` **to the backend process**, never to React:

```bash
export GITHUB_TOKEN=your_token_here
python -m uvicorn app.main:app --reload
```

Do **not** store your real token in Git or put it in a `VITE_` variable. `.env.example` documents optional local configuration; this project does not automatically load `.env` files.

## Tests

```bash
python -m pytest -v
cd web && npm run build
```

The backend tests mock GitHub responses and use a temporary SQLite database.

## Containers and Cloud Run

```bash
docker build -t prism .
docker run --rm -p 8080:8080 prism
```

Then open http://localhost:8080/. A Docker image serves the compiled dashboard and FastAPI from a single server.

For a **stateless demonstration** on Google Cloud Run (after installing `gcloud`, selecting a Google Cloud project, enabling billing and required APIs, and configuring permissions):

```bash
gcloud run deploy prism --source . --region us-central1 --allow-unauthenticated
```

Google Cloud builds the checked-in `Dockerfile` for this source deployment. Do not expose a GitHub token in the command line; use Secret Manager if needed. Verify billing and costs before deploying.

**Do not treat SQLite snapshots stored on Cloud Run as durable**: Cloud Run instances are disposable and may run in parallel. Production snapshot history requires a managed database (such as Cloud SQL). This starter is intended to work **locally** first. Cloud Run can host it as a stateless demo, but history there is temporary.

## Code structure

```text
app/
  main.py             FastAPI routes, error handling, and caching orchestration
  github_client.py    Async GitHub REST client and upstream error mapping
  analytics.py        Pure functions to compute analytics from sampled data
  storage.py          Local SQLite snapshots
web/src/
  App.tsx             Dashboard composition and state
  components/         Charts, reusable UI components
  lib/format.ts       Repository parsing and display formatting
  types.ts            TypeScript API response types
tests/                Deterministic automated tests
.github/workflows/    CI pipeline
```

For a guided module-by-module setup, see [BUILD_IN_STAGES.md](BUILD_IN_STAGES.md).

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Health check |
| `GET /repos/{owner}/{repo}` | Original simple repository endpoint |
| `GET /api/repositories/{owner}/{repo}/overview` | Repository analytics, cached for 10 minutes |
| `GET /api/repositories/{owner}/{repo}/overview?refresh=true` | Fetch live metrics and save a snapshot |
| `GET /api/repositories/{owner}/{repo}/history` | Saved local snapshots |
| `GET /api/repositories/recent` | Recently analyzed repositories |

## Current limits and next improvements

- Public repositories only; no private GitHub account integration or OAuth yet.
- Single-page REST calls, not lifetime trends or comprehensive productivity measures.
- Local SQLite snapshots; no production-grade multi-instance database.
- No GitHub webhooks, permissions system, alerting, or distributed processing yet.
- No performance benchmark claims without measured evidence.

PRISM is a portfolio-sized MVP, not a comprehensive developer performance monitoring service. Commit counts and PR timing alone should not be used to evaluate individual engineers.
