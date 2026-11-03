import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import type { Overview, Snapshot, Recent } from './types';
import Icon from './components/Icon';
import ActivityChart from './components/ActivityChart';
import MiniLine from './components/MiniLine';
import PrRow from './components/PrRow';
import StatCard from './components/StatCard';
import { abbrev, ago, parseRepo } from './lib/format';
const SUGGESTIONS = ['google/guava', 'fastapi/fastapi', 'facebook/react'];
export default function App() {
    const [input, setInput] = useState('google/guava');
    const [current, setCurrent] = useState('google/guava');
    const [overview, setOverview] = useState<Overview | null>(null);
    const [history, setHistory] = useState<Snapshot[]>([]);
    const [recent, setRecent] = useState<Recent[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [tab, setTab] = useState<'overview' | 'history'>('overview');
    async function load(name: string, refresh = false) {
        setLoading(true);
        setError('');
        const parts = parseRepo(name);
        if (!parts) {
            setLoading(false);
            setError('Enter owner/repo or a public GitHub repository URL.');
            return;
        }
        setCurrent(parts);
        setInput(parts);
        const [owner, repo] = parts.split('/');
        try {
            const response = await fetch(`/api/repositories/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/overview${refresh ? '?refresh=true' : ''}`);
            if (!response.ok) {
                let detail = `Request failed (${response.status}).`;
                try {
                    const body = await response.json();
                    if (typeof body.detail === 'string')
                        detail = body.detail;
                }
                catch { /* fall back */ }
                throw new Error(detail);
            }
            const body: Overview = await response.json();
            setOverview(body);
            const [hist, recents] = await Promise.all([
                fetch(`/api/repositories/${owner}/${repo}/history`).then(x => x.ok ? x.json() : { snapshots: [] }),
                fetch('/api/repositories/recent').then(x => x.ok ? x.json() : { repositories: [] }),
            ]);
            setHistory(hist.snapshots || []);
            setRecent(recents.repositories || []);
        }
        catch (e) {
            setOverview(null);
            setHistory([]);
            setError(e instanceof Error ? e.message : 'Unexpected error');
        }
        finally {
            setLoading(false);
        }
    }
    useEffect(() => { void load('google/guava'); }, []);
    function onSearch(e: FormEvent) { e.preventDefault(); void load(input); }
    const m = overview?.metrics, r = overview?.repository;
    const statuses = overview?.pull_requests ?? [];
    const merged = statuses.filter(p => p.status === 'merged').length;
    const open = statuses.filter(p => p.status === 'open').length;
    const closed = statuses.filter(p => p.status === 'closed').length;
    const total = Math.max(1, statuses.length);
    return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><span>◈</span></div><span className="brand-word">prism<span className="brand-dot">.</span></span></div>
      <div className="side-label">WORKSPACE</div>
      <button className={`side-link ${tab === 'overview' ? 'active' : ''}`} onClick={() => setTab('overview')}><Icon name="bars" size={18}/> Overview</button>
      <button className={`side-link ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}><Icon name="database" size={18}/> Snapshots</button>
      <a className="side-link" href="/docs" target="_blank" rel="noreferrer"><Icon name="code" size={18}/> API documentation <span className="side-ext"><Icon name="external" size={13}/></span></a>
      <div className="side-label recent-label">RECENTLY VIEWED</div>
      <div className="recent-list">
        {recent.length ? recent.map(item => <button key={item.full_name} className="recent-link" onClick={() => void load(item.full_name)}><span className="repo-dot"/>{item.full_name}</button>) : <span className="recent-empty">Repositories appear here after analysis.</span>}
      </div>
      <div className="sidebar-bottom">
        <div className="version"><span className="online-pulse"/> API v1.0 · Local workspace</div>
        <div className="side-hint">Built for better engineering decisions, one repository at a time.</div>
      </div>
    </aside>

    <main className="main">
      <header className="topbar"><div className="crumb">Workspace <span>/</span> <strong>{tab === 'overview' ? 'Overview' : 'Snapshots'}</strong></div><span className="top-version"><span className="small-dot"/> Developer intelligence</span></header>
      <div className="content">
        <section className="welcome"><div className="eyebrow"><span className="eyebrow-line"/> UNDERSTAND YOUR CODEBASE</div>
          <h1>{tab === 'overview' ? <>Engineering insights, <em>in focus.</em></> : <>Your history, <em>in focus.</em></>}</h1>
          <p>Explore real GitHub repository activity, pull request patterns, and development signals—all in one place.</p>
        </section>

        <form className="search-card" onSubmit={onSearch}>
          <div className="search-main"><Icon name="search" size={21}/><input aria-label="GitHub repository" value={input} onChange={e => setInput(e.target.value)} placeholder="owner/repository or GitHub URL"/><button type="submit" className="analyze-btn" disabled={loading}>{loading ? 'Analyzing…' : 'Analyze repo'} <Icon name="arrow" size={17}/></button></div>
          <div className="search-footer"><span>TRY A REPOSITORY</span>{SUGGESTIONS.map(s => <button type="button" className="suggestion" key={s} onClick={() => void load(s)}>{s}</button>)}</div>
        </form>

        {error && <div className="alert error" role="alert"><strong>Couldn't load repository</strong><span>{error}</span><button onClick={() => void load(current)}>Try again</button></div>}
        {loading && <div className="loading"><span className="spinner"/> Contacting GitHub and analyzing the latest repository data…</div>}

        {!loading && overview && r && m && <>
          <div className="section-heading"><div className="repo-identity"><span className="repo-avatar"><Icon name="code" size={22}/></span><div><div className="repo-name">{r.full_name} <a href={r.url} target="_blank" rel="noreferrer" aria-label="View repository on GitHub"><Icon name="external" size={17}/></a></div><p>{r.description || 'No description provided'}</p></div></div><button type="button" className="refresh-btn" onClick={() => void load(current, true)}><Icon name="refresh" size={16}/> Refresh data</button></div>
          <div className="repo-tags"><span className="pill"><span className="tiny-circle"/>{r.language ?? 'Unknown language'}</span><span className="pill"><Icon name="git" size={13}/> {r.default_branch || 'main'}</span><span className="pill"><Icon name="star" size={13}/>{abbrev(r.stars)} stars</span><span className="pill"><Icon name="branch" size={13}/>{abbrev(r.forks)} forks</span><span className="meta-time">{overview.source === 'cache' ? 'Cached' : 'Updated'} {ago(overview.fetched_at)}</span></div>

          {tab === 'overview' ? <>
            <div className="stats-grid">
              <StatCard title="Commits in sample" value={abbrev(m.sampled_commits)} sub="Up to 100 recent commits" icon="git" accent="stat-green"/>
              <StatCard title="PRs in sample" value={abbrev(m.sampled_pull_requests)} sub={`${m.open_prs_in_sample} currently open in sample`} icon="branch"/>
              <StatCard title="Merged / closed" value={m.sampled_closed_pr_merge_rate_pct === null ? '—' : `${m.sampled_closed_pr_merge_rate_pct}%`} sub="Among sampled closed PRs" icon="shield"/>
              <StatCard title="Avg. time to merge" value={m.avg_merge_hours === null ? '—' : m.avg_merge_hours < 48 ? `${m.avg_merge_hours}h` : `${(m.avg_merge_hours / 24).toFixed(1)}d`} sub="For sampled merged PRs" icon="clock"/>
            </div>

            <div className="two-column">
              <section className="panel activity-panel"><div className="panel-top"><div><div className="panel-kicker">ACTIVITY</div><h2>Commit velocity</h2><p>Sampled commits over the last 14 days · UTC</p></div><span className="chart-pill">14 days</span></div><ActivityChart data={overview.activity}/><div className="panel-bottom"><span><span className="legend-square"/> Sampled commits</span><strong>{m.sampled_commits_last_14_days} <small>in the last 14 days</small></strong></div></section>
              <section className="panel breakdown-panel"><div className="panel-top"><div><div className="panel-kicker">WORKFLOW</div><h2>Pull request status</h2><p>15 most recent PRs from the sample</p></div></div>
                <div className="donut-row"><div className="donut" style={{ background: `conic-gradient(#b8f48d 0 ${merged / total * 100}%, #93a5ee ${merged / total * 100}% ${(merged + open) / total * 100}%, #eaa879 ${(merged + open) / total * 100}% 100%)` }}><div className="donut-hole"><b>{statuses.length}</b><small>displayed</small></div></div><div className="donut-legend"><div><span className="legend-dot merged"/>Merged <b>{merged}</b></div><div><span className="legend-dot open"/>Open <b>{open}</b></div><div><span className="legend-dot closed"/>Closed <b>{closed}</b></div></div></div>
                <div className="small-insight"><Icon name="people" size={18}/><div><strong>{m.unique_commit_authors_in_sample}</strong><span>identified authors across sampled commits</span></div></div>
              </section>
            </div>

            <section className="panel pull-panel"><div className="panel-top"><div><div className="panel-kicker">PULL REQUESTS</div><h2>Recent contributions</h2><p>The 15 newest pull requests, sorted by creation date</p></div><a href={`${r.url}/pulls`} target="_blank" rel="noreferrer" className="view-github">View on GitHub <Icon name="external" size={15}/></a></div>
              <div className="pr-list">{statuses.length ? statuses.map(pr => <PrRow key={pr.number} pr={pr}/>) : <div className="empty-small">No pull requests found in this sample.</div>}</div>
            </section>
          </> : <div className="two-column history-grid"><section className="panel"><div className="panel-top"><div><div className="panel-kicker">PERSISTED DATA</div><h2>Stars over time</h2><p>Saved local snapshots—not interpolated data</p></div></div><MiniLine data={history}/><div className="history-footer">{history.length} snapshot{history.length === 1 ? '' : 's'} saved</div></section><section className="panel"><div className="panel-top"><div><div className="panel-kicker">HISTORY</div><h2>Saved snapshots</h2><p>Each refresh adds a new local record</p></div></div><div className="history-list">{history.length ? [...history].reverse().map((snap, i) => <div className="history-row" key={`${snap.fetched_at}-${i}`}><span>{new Date(snap.fetched_at).toLocaleString()}</span><strong>{abbrev(snap.stars)} stars</strong></div>) : <div className="empty-small">No saved snapshots yet.</div>}</div></section></div>}

          <div className="sample-note"><Icon name="shield" size={18}/><span><strong>Data methodology:</strong> {overview.sample_note} GitHub's repository-wide star and fork counts are metadata, not sampled metrics.</span></div>
        </>}
        <footer className="footer"><span>◈ PRISM · Pull Request Insights & Software Metrics</span><span>Built with FastAPI, React & GitHub REST API</span></footer>
      </div>
    </main>
  </div>;
}
