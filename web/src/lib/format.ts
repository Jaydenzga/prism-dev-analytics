export function abbrev(value: number): string {
    if (value >= 1000000)
        return `${(value / 1000000).toFixed(1)}m`;
    if (value >= 10000)
        return `${(value / 1000).toFixed(1)}k`;
    return Intl.NumberFormat('en-US').format(value);
}
export function ago(date: string): string {
    const delta = Date.now() - new Date(date).getTime();
    if (!Number.isFinite(delta))
        return 'recently';
    if (delta < 60000)
        return 'just now';
    if (delta < 3600000)
        return `${Math.floor(delta / 60000)}m ago`;
    if (delta < 86400000)
        return `${Math.floor(delta / 3600000)}h ago`;
    return `${Math.floor(delta / 86400000)}d ago`;
}
export function parseRepo(value: string): string | null {
    const raw = value.trim().replace(/\/$/, '');
    let path = raw;
    if (/^https?:\/\//i.test(raw)) {
        try {
            const url = new URL(raw);
            if (!['github.com', 'www.github.com'].includes(url.hostname.toLowerCase()))
                return null;
            path = url.pathname.replace(/^\//, '').replace(/\/$/, '');
        }
        catch {
            return null;
        }
    }
    const parts = path.split('/');
    if (parts.length !== 2)
        return null;
    const [owner, repo] = parts;
    if (!/^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$/.test(owner))
        return null;
    if (!/^[a-zA-Z0-9_.-]{1,100}$/.test(repo) || repo === '.' || repo === '..')
        return null;
    return `${owner}/${repo}`;
}
