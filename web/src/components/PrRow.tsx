import type { PullRequest } from '../types';
import Icon from './Icon';
import { ago } from '../lib/format';
export default function PrRow({ pr }: {
    pr: PullRequest;
}) {
    return <a className="pr-row" href={pr.url} target="_blank" rel="noreferrer">
    <span className={`pr-icon ${pr.status}`}><Icon name="branch" size={17}/></span>
    <span className="pr-title"><span>{pr.title}</span><small>#{pr.number} · {pr.author} · opened {ago(pr.created_at)}</small></span>
    <span className={`status ${pr.status}`}>{pr.draft && pr.status === 'open' ? 'Draft' : pr.status}</span>
    <span className="pr-external"><Icon name="external" size={16}/></span>
  </a>;
}
