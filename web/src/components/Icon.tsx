import type { ReactNode } from 'react';
export default function Icon({ name, size = 20 }: {
    name: string;
    size?: number;
}) {
    const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.7, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
    const paths: Record<string, ReactNode> = {
        search: <><circle cx="10.7" cy="10.7" r="7.1"/><path d="m16 16 5 5"/></>,
        arrow: <><path d="M5 12h14m-7-7 7 7-7 7"/></>,
        external: <><path d="M12 5h7v7M19 5l-9 9"/><path d="M19 13v6H5V5h6"/></>,
        refresh: <><path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.7 8a8 8 0 0 1 13.4 1l.9 3M4 12l.9 3a8 8 0 0 0 13.4 1"/></>,
        branch: <><circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="7" r="2"/><path d="M6 7v10M18 9a8 8 0 0 1-8 8H6"/></>,
        star: <path d="m12 2.8 2.9 5.9 6.5 1-4.7 4.6 1.1 6.5-5.8-3.1-5.8 3.1 1.1-6.5-4.7-4.6 6.5-1z"/>,
        git: <><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M8 6h8M12 16V6"/></>,
        clock: <><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></>,
        people: <><circle cx="9" cy="8" r="3"/><path d="M2.5 20c0-4 2-6 6.5-6s6.5 2 6.5 6"/><path d="M17 5c3.5.1 4.5 5.7 1 6.6M18 14c2.5.5 4 2.3 4 6"/></>,
        bars: <><rect x="3" y="11" width="4" height="10" rx="1"/><rect x="10" y="6" width="4" height="15" rx="1"/><rect x="17" y="2" width="4" height="19" rx="1"/></>,
        database: <><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/></>,
        bolt: <path d="m13 2-9 11h7l-1 9 10-12h-7z"/>,
        shield: <><path d="M12 2 4 5v6c0 5.5 3.2 8.8 8 11 4.8-2.2 8-5.5 8-11V5z"/><path d="m9 12 2 2 4-4"/></>,
        circle: <circle cx="12" cy="12" r="9"/>,
        code: <><path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-14-2 18"/></>,
    };
    return <svg {...common} aria-hidden="true">{paths[name] ?? paths.circle}</svg>;
}
