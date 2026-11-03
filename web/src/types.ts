export interface Repository {
    full_name: string;
    description: string | null;
    url: string;
    stars: number;
    forks: number;
    open_issues: number;
    language: string | null;
    default_branch: string;
    avatar_url: string | null;
}
export interface Metrics {
    sampled_pull_requests: number;
    sampled_commits: number;
    open_prs_in_sample: number;
    merged_prs_in_sample: number;
    sampled_closed_pr_merge_rate_pct: number | null;
    avg_merge_hours: number | null;
    unique_commit_authors_in_sample: number;
    sampled_commits_last_14_days: number;
}
export interface PullRequest {
    number: number;
    title: string;
    status: 'open' | 'closed' | 'merged';
    draft: boolean;
    author: string;
    url: string;
    created_at: string;
    merged_at: string | null;
}
export interface Overview {
    repository: Repository;
    metrics: Metrics;
    activity: {
        date: string;
        count: number;
    }[];
    pull_requests: PullRequest[];
    sample_note: string;
    fetched_at: string;
    source: 'live' | 'cache';
}
export interface Snapshot {
    fetched_at: string;
    stars: number;
    forks: number;
    sampled_commits: number;
}
export interface Recent {
    full_name: string;
    fetched_at: string;
}
