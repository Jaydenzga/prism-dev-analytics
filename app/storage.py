"""Local SQLite history for PRISM; Cloud Run requires external storage for durability."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def database_path() -> Path:
    return Path(os.getenv("PRISM_DB_PATH", "data/prism.db"))


def connect():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            payload TEXT NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS snapshots_repo_idx ON snapshots(full_name, id DESC)")


def save_snapshot(full_name: str, payload: dict) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            "INSERT INTO snapshots (full_name, fetched_at, payload) VALUES (?, ?, ?)",
            (full_name.lower(), payload["fetched_at"], json.dumps(payload)),
        )
        # Keep last 30 snapshots per repo to limit local storage growth.
        conn.execute("""DELETE FROM snapshots WHERE full_name = ? AND id NOT IN (
            SELECT id FROM snapshots WHERE full_name = ? ORDER BY id DESC LIMIT 30
        )""", (full_name.lower(), full_name.lower()))


def latest_snapshot(full_name: str) -> dict | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT payload FROM snapshots WHERE full_name = ? ORDER BY id DESC LIMIT 1",
            (full_name.lower(),),
        ).fetchone()
    return json.loads(row["payload"]) if row else None


def history(full_name: str, limit: int = 20) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT payload FROM snapshots WHERE full_name = ? ORDER BY id DESC LIMIT ?",
            (full_name.lower(), limit),
        ).fetchall()
    return [
        {"fetched_at": item["fetched_at"], "stars": item["repository"]["stars"],
         "forks": item["repository"]["forks"], "sampled_commits": item["metrics"]["sampled_commits"]}
        for row in reversed(rows) for item in [json.loads(row["payload"])]
    ]


def recent_repositories(limit: int = 8) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute("""SELECT s.full_name, s.fetched_at FROM snapshots s
            WHERE s.id IN (SELECT MAX(id) FROM snapshots GROUP BY full_name)
            ORDER BY s.id DESC LIMIT ?""", (limit,)).fetchall()
    return [dict(row) for row in rows]


def is_fresh(payload: dict, ttl_seconds: int = 600) -> bool:
    try:
        when = datetime.fromisoformat(payload["fetched_at"].replace("Z", "+00:00"))
        delta = (datetime.now(timezone.utc) - when).total_seconds()
        return 0 <= delta < ttl_seconds
    except (ValueError, KeyError, TypeError):
        return False
