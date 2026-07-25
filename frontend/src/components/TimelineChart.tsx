'use client';

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import type { TimelinePoint } from '@/lib/types';
import { format, parseISO } from 'date-fns';

interface TimelineChartProps {
  data: TimelinePoint[];
  loading?: boolean;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-strong)',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: 12,
    }}>
      <p style={{ color: 'var(--text-muted)', marginBottom: 6 }}>{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color, fontWeight: 600 }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

export default function TimelineChart({ data, loading }: TimelineChartProps) {
  if (loading) {
    return <div className="skeleton" style={{ height: 220, borderRadius: 8 }} />;
  }

  const formatted = data.map(d => ({
    ...d,
    label: d.timestamp
      ? (() => { try { return format(parseISO(d.timestamp), 'HH:mm'); } catch { return d.timestamp; } })()
      : '',
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={formatted} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
        <defs>
          <linearGradient id="gradEvents" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#00d4ff" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gradAlerts" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#475569' }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 10, fill: '#475569' }} tickLine={false} axisLine={false} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
        <Area type="monotone" dataKey="events" name="Events" stroke="#00d4ff" strokeWidth={2} fill="url(#gradEvents)" dot={false} />
        <Area type="monotone" dataKey="alerts" name="Alerts" stroke="#ef4444" strokeWidth={2} fill="url(#gradAlerts)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
