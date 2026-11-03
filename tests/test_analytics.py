from datetime import datetime, timezone
from app.analytics import build_overview

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def test_metrics_from_sample():
    repo = {"full_name": "google/guava", "stargazers_count": 42, "forks_count": 7, "owner": {}}
    pulls = [
        {"number": 1, "title": "Feature", "state": "closed", "created_at": "2026-10-24T00:00:00Z", "merged_at": "2026-10-25T00:00:00Z", "user": {"login": "dev"}},
        {"number": 2, "state": "open", "created_at": "2026-10-25T00:00:00Z", "merged_at": None},
    ]
    commits = [
        {"author": {"login": "dev"}, "commit": {"committer": {"date": "2026-10-26T10:00:00Z"}}},
        {"author": {"login": "dev"}, "commit": {"committer": {"date": "2026-10-26T09:00:00Z"}}},
    ]
    overview = build_overview(repo, pulls, commits, now=NOW)
    assert overview["metrics"]["sampled_pull_requests"] == 2
    assert overview["metrics"]["sampled_closed_pr_merge_rate_pct"] == 100
    assert overview["metrics"]["avg_merge_hours"] == 24
    assert overview["metrics"]["unique_commit_authors_in_sample"] == 1
    assert overview["metrics"]["sampled_commits_last_14_days"] == 2
    assert overview["activity"][-1]["count"] == 2


def test_empty_repo_samples_are_safe():
    overview = build_overview({"full_name": "user/empty", "owner": {}}, [], [], now=NOW)
    assert overview["metrics"]["avg_merge_hours"] is None
    assert overview["metrics"]["sampled_closed_pr_merge_rate_pct"] is None
    assert len(overview["activity"]) == 14
