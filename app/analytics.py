"""Pure GitHub data transformations; suitable for deterministic unit tests."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from statistics import mean


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def build_overview(repository: dict, pulls: list[dict], commits: list[dict], now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    now = now.astimezone(timezone.utc)
    end_date = now.date()
    first_date = end_date - timedelta(days=13)
    commit_counts: Counter[str] = Counter()
    contributors: set[str] = set()

    for commit in commits:
        info = commit.get("commit") or {}
        author = commit.get("author") or {}
        identity = author.get("login") or (info.get("author") or {}).get("email")
        if identity:
            contributors.add(str(identity).lower())
        committed_at = parse_time((info.get("committer") or {}).get("date"))
        if committed_at and first_date <= committed_at.date() <= end_date:
            commit_counts[committed_at.date().isoformat()] += 1

    timeline = [
        {"date": (first_date + timedelta(days=i)).isoformat(), "count": commit_counts[(first_date + timedelta(days=i)).isoformat()]}
        for i in range(14)
    ]
    pull_rows = []
    merge_hours = []
    for item in pulls:
        created = parse_time(item.get("created_at"))
        merged = parse_time(item.get("merged_at"))
        status = "merged" if merged else ("open" if item.get("state") == "open" else "closed")
        if created and merged and merged >= created:
            merge_hours.append((merged - created).total_seconds() / 3600)
        pull_rows.append({
            "number": item.get("number"),
            "title": item.get("title") or "Untitled pull request",
            "status": status,
            "draft": bool(item.get("draft")),
            "author": (item.get("user") or {}).get("login") or "unknown",
            "url": item.get("html_url"),
            "created_at": item.get("created_at"),
            "merged_at": item.get("merged_at"),
        })

    merged_n = sum(row["status"] == "merged" for row in pull_rows)
    closed_n = sum(row["status"] != "open" for row in pull_rows)
    return {
        "repository": {
            "full_name": repository.get("full_name"),
            "description": repository.get("description"),
            "url": repository.get("html_url"),
            "stars": repository.get("stargazers_count", 0),
            "forks": repository.get("forks_count", 0),
            "open_issues": repository.get("open_issues_count", 0),
            "language": repository.get("language"),
            "default_branch": repository.get("default_branch"),
            "avatar_url": (repository.get("owner") or {}).get("avatar_url"),
        },
        "metrics": {
            "sampled_pull_requests": len(pulls),
            "sampled_commits": len(commits),
            "open_prs_in_sample": sum(row["status"] == "open" for row in pull_rows),
            "merged_prs_in_sample": merged_n,
            "sampled_closed_pr_merge_rate_pct": round((merged_n / closed_n) * 100, 1) if closed_n else None,
            "avg_merge_hours": round(mean(merge_hours), 1) if merge_hours else None,
            "unique_commit_authors_in_sample": len(contributors),
            "sampled_commits_last_14_days": sum(point["count"] for point in timeline),
        },
        "activity": timeline,
        "pull_requests": pull_rows[:15],
        "sample_note": "PR metrics use at most the 100 newest PRs. Commit metrics use at most the 100 newest commits on the default branch. These are not lifetime totals, and the 14-day chart may undercount busy repositories.",
        "fetched_at": now.isoformat().replace("+00:00", "Z"),
        "source": "live",
    }