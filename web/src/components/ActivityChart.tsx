import type { Overview } from '../types';
export default function ActivityChart({ data }: {
    data: Overview['activity'];
}) {
    const top = Math.max(4, ...data.map(x => x.count));
    const h = 182;
    const barSpace = 56;
    return <div className="chart-wrap" role="img" aria-label="Sampled commit activity for the last fourteen days">
    <svg viewBox="0 0 850 258" preserveAspectRatio="xMidYMid meet" className="activity-svg">
      {[0, .25, .5, .75, 1].map((t) => <g key={t}><line x1="47" y1={24 + h * t} x2="834" y2={24 + h * t} stroke="#26313b" strokeDasharray={t === 1 ? '0' : '4 7'}/><text x="30" y={28 + h * t} fill="#7e8b95" fontSize="12" textAnchor="end">{Math.round(top * (1 - t))}</text></g>)}
      {data.map((point, i) => {
            const barH = Math.max(point.count > 0 ? 6 : 2, point.count / top * h);
            const x = 62 + i * barSpace;
            return <g key={point.date}>
          <rect x={x} y={24 + h - barH} width="28" height={barH} rx="5" fill={i === data.length - 1 ? '#c7ff92' : '#79c8ad'} opacity={point.count ? 1 : .2}/>
          <title>{`${point.date}: ${point.count} sampled commits`}</title>
          {(i % 2 === 0 || i === 13) && <text x={x + 14} y="240" textAnchor="middle" fill="#89949e" fontSize="12">{new Date(point.date + 'T12:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })}</text>}
        </g>;
        })}
    </svg>
  </div>;
}
