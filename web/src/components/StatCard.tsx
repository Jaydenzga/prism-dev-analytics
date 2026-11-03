import Icon from './Icon';
export default function StatCard({ title, value, sub, icon, accent = '' }: {
    title: string;
    value: string;
    sub: string;
    icon: string;
    accent?: string;
}) {
    return <article className={`stat-card ${accent}`}>
    <div className="stat-top"><span>{title}</span><span className="stat-icon"><Icon name={icon} size={19}/></span></div>
    <div className="stat-value">{value}</div>
    <div className="stat-foot">{sub}</div>
  </article>;
}
