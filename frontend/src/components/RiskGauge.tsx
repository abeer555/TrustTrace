'use client';

import { getRiskLevel, getRiskColor, formatRiskScore } from '@/lib/utils';

interface RiskGaugeProps {
  score: number;
  size?: number;
  showLabel?: boolean;
}

export default function RiskGauge({ score, size = 80, showLabel = true }: RiskGaugeProps) {
  const level = getRiskLevel(score);
  const color = getRiskColor(score);
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const filled = circumference * score;
  const gap = circumference - filled;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Track */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={8}
          />
          {/* Fill */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none"
            stroke={color}
            strokeWidth={8}
            strokeLinecap="round"
            strokeDasharray={`${filled} ${gap}`}
            className="risk-gauge-ring"
            style={{ filter: `drop-shadow(0 0 6px ${color})` }}
          />
        </svg>
        {/* Center text */}
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: size * 0.18, fontWeight: 700, color, lineHeight: 1 }}>
            {Math.round(score * 100)}
          </span>
          <span style={{ fontSize: size * 0.11, color: 'var(--text-muted)', lineHeight: 1 }}>/ 100</span>
        </div>
      </div>
      {showLabel && (
        <span
          className={`risk-badge ${level}`}
          style={{ fontSize: 10 }}
        >
          {level.toUpperCase()}
        </span>
      )}
    </div>
  );
}
