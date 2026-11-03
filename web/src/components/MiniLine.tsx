import type { Snapshot } from '../types';
export default function MiniLine({ data }: {
    data: Snapshot[];
}) {
    if (data.length < 2)
        return <div className="empty-small">Refresh this repository later to see changes over time.</div>;
    const nums = data.map(x => x.stars);
    const min = Math.min(...nums), max = Math.max(...nums);
    const range = Math.max(1, max - min);
    const coords = nums.map((v, i) => `${20 + i / (nums.length - 1) * 300},${105 - ((v - min) / range) * 75}`).join(' ');
    return <svg viewBox="0 0 340 130" className="mini-line" aria-label="Star counts across saved snapshots" role="img">
    <defs><linearGradient id="line-shade" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#a3f4b6" stopOpacity=".22"/><stop offset="100%" stopColor="#a3f4b6" stopOpacity="0"/></linearGradient></defs>
    <polygon points={`20,120 ${coords} 320,120`} fill="url(#line-shade)"/>
    <polyline points={coords} fill="none" stroke="#b6f78b" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
    {nums.map((v, i) => <circle key={i} cx={20 + i / (nums.length - 1) * 300} cy={105 - ((v - min) / range) * 75} r="3" fill="#d3ffb0"/>)}
  </svg>;
}
