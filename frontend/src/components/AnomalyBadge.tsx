'use client';

import { getAnomalyColor, getAnomalyLabel } from '@/lib/utils';

interface AnomalyBadgeProps {
  type: string;
  size?: 'sm' | 'md';
}

export default function AnomalyBadge({ type, size = 'md' }: AnomalyBadgeProps) {
  const color = getAnomalyColor(type);
  const label = getAnomalyLabel(type);
  const isNormal = type === 'normal';

  return (
    <span
      className="anomaly-badge"
      style={{
        background: `${color}1a`,
        color: color,
        border: `1px solid ${color}44`,
        fontSize: size === 'sm' ? 10 : 11,
        padding: size === 'sm' ? '2px 8px' : '3px 10px',
      }}
    >
      {!isNormal && (
        <span style={{ width: 5, height: 5, borderRadius: '50%', background: color, display: 'inline-block', marginRight: 4 }} />
      )}
      {label}
    </span>
  );
}
