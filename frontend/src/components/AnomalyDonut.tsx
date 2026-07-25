'use client';

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { ANOMALY_COLORS, ANOMALY_LABELS } from '@/lib/utils';

interface AnomalyDonutProps {
  data: Record<string, number>;
  loading?: boolean;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const { name, value } = payload[0];
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-strong)',
      borderRadius: 8, padding: '8px 12px', fontSize: 12,
    }}>
      <p style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{ANOMALY_LABELS[name] || name}</p>
      <p style={{ color: 'var(--text-muted)' }}>{value} alerts</p>
    </div>
  );
};

export default function AnomalyDonut({ data, loading }: AnomalyDonutProps) {
  if (loading) return <div className="skeleton" style={{ height: 220, borderRadius: 8 }} />;

  const chartData = Object.entries(data)
    .filter(([k]) => k !== 'normal' && k)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  if (!chartData.length) {
    return (
      <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
        No anomalies detected yet
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%" cy="50%"
          innerRadius={55} outerRadius={85}
          paddingAngle={3}
          dataKey="value"
        >
          {chartData.map((entry) => (
            <Cell
              key={entry.name}
              fill={ANOMALY_COLORS[entry.name] || '#6b7280'}
              stroke="transparent"
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          formatter={(value) => (
            <span style={{ fontSize: 11, color: '#94a3b8' }}>
              {ANOMALY_LABELS[value] || value}
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
