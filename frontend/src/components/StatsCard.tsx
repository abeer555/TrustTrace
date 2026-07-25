'use client';

import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  accent: 'cyan' | 'red' | 'purple' | 'green';
  trend?: { value: string; up: boolean };
  loading?: boolean;
}

export default function StatsCard({ title, value, subtitle, icon: Icon, accent, trend, loading }: StatsCardProps) {
  const accentColors = {
    cyan:   '#00d4ff',
    red:    '#ef4444',
    purple: '#a855f7',
    green:  '#10b981',
  };
  const color = accentColors[accent];

  return (
    <div className={`glass-card stat-card ${accent} animate-fade-up`} style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 8 }}>
            {title}
          </p>
          {loading ? (
            <div className="skeleton" style={{ height: 32, width: 100, marginBottom: 6 }} />
          ) : (
            <p style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-1px', lineHeight: 1 }}>
              {value}
            </p>
          )}
          {subtitle && (
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>{subtitle}</p>
          )}
          {trend && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 8 }}>
              <span style={{ fontSize: 11, color: trend.up ? '#ef4444' : '#10b981', fontWeight: 600 }}>
                {trend.up ? '↑' : '↓'} {trend.value}
              </span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>vs last period</span>
            </div>
          )}
        </div>
        <div style={{
          width: 44, height: 44, borderRadius: 10,
          background: `${color}18`,
          border: `1px solid ${color}33`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <Icon size={20} color={color} />
        </div>
      </div>
    </div>
  );
}
