# PRISM module-by-module build guide

You can copy these modules into the repository you already created in your earlier lessons. **You do not need to delete that repository or replace its Git history.** Read each file, run a quick check, and make your own improvements as you go. Do not create a fictional development history.

## Module 1 — Backend and GitHub API

Copy the provided `app/` folder and `requirements.txt` into your repository. This replaces the simple lesson-two backend with a slightly larger, still readable implementation.

- `app/main.py` — incoming API requests, status codes, and routing
- `app/github_client.py` — sends GitHub API requests using HTTPX
- `app/analytics.py` — calculates summary metrics, without network calls
- `app/storage.py` — SQLite caching and saved snapshots

Run:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Check `/health`, `/repos/google/guava`, and `/api/repositories/google/guava/overview` via http://127.0.0.1:8000/docs.

## Module 2 — Dashboard

Copy `web/` into the same repository. The frontend is separated into one page, reusable components, utility functions, and shared types.

```bash
cd web
npm install
npm run dev
```

Open http://127.0.0.1:5173. Choose a repository and watch the results load. The backend must still be running in another terminal.

## Module 3 — Tests and GitHub Actions

Copy `tests/` and `.github/workflows/ci.yml`.

```bash
python -m pytest -v
cd web && npm run build
```

When those checks pass on your Mac, review the changes using `git diff` or `git status`. Commit work you actually reviewed and ran. Example description: `Add GitHub repository analytics API and dashboard`.

## Module 4 — Container and documentation

Copy `Dockerfile`, `.dockerignore`, `.gitignore`, `.env.example`, and `README.md`. You can use Docker locally if installed. The Cloud Run section in the README documents the limitations of SQLite on disposable containers.

## After assembly

Open the app, try two public repositories, check the sample-data note, and refresh to save a second snapshot. Run tests again, then update the README with screenshots and your own explanation of the architecture.

**When we study the code:** start with `github_client.py` and `main.py`, follow a request through `analytics.py` into `storage.py`, and finish with React's `App.tsx` and tests. This keeps the learning focused on what the real program does.
