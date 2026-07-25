'use client';

import { useState } from 'react';
import { format, parseISO } from 'date-fns';
import { Eye, CheckCircle, ChevronRight, Filter } from 'lucide-react';
import type { AlertItem } from '@/lib/types';
import AnomalyBadge from './AnomalyBadge';
import RiskGauge from './RiskGauge';
import { getRiskLevel } from '@/lib/utils';

interface AlertTableProps {
  alerts: AlertItem[];
  loading?: boolean;
  onSelect: (alert: AlertItem) => void;
  onReview?: (id: number) => void;
}

export default function AlertTable({ alerts, loading, onSelect, onReview }: AlertTableProps) {
  const [filter, setFilter] = useState('');

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 52, borderRadius: 8 }} />
        ))}
      </div>
    );
  }

  const filtered = alerts.filter(a =>
    !filter ||
    a.entity_id.toLowerCase().includes(filter.toLowerCase()) ||
    a.anomaly_type.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      {/* Filter bar */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 14, alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Filter size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            className="tt-input"
            placeholder="Filter by entity or anomaly type…"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{ width: '100%', paddingLeft: 30 }}
          />
        </div>
        <span style={{ fontSize: 12, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
          {filtered.length} alert{filtered.length !== 1 ? 's' : ''}
        </span>
      </div>

      <table className="tt-table">
        <thead>
          <tr>
            <th>Risk</th>
            <th>Entity</th>
            <th>Anomaly Type</th>
            <th>Top Signal</th>
            <th>Timestamp</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(alert => {
            const level = getRiskLevel(alert.risk_score);
            return (
              <tr
                key={alert.id}
                className={alert.is_reviewed ? 'reviewed' : ''}
                onClick={() => onSelect(alert)}
              >
                <td>
                  <RiskGauge score={alert.risk_score} size={44} showLabel={false} />
                </td>
                <td>
                  <span className="entity-pill">{alert.entity_id}</span>
                </td>
                <td>
                  <AnomalyBadge type={alert.anomaly_type} />
                </td>
                <td style={{ color: 'var(--text-secondary)', fontSize: 12, maxWidth: 220 }}>
                  <span style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}>
                    {alert.top_factor}
                  </span>
                </td>
                <td style={{ color: 'var(--text-muted)', fontSize: 12, fontFamily: 'JetBrains Mono, monospace' }}>
                  {(() => {
                    try { return format(parseISO(alert.timestamp), 'MMM d, HH:mm:ss'); }
                    catch { return alert.timestamp; }
                  })()}
                </td>
                <td>
                  {alert.is_reviewed ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: '#10b981' }}>
                      <CheckCircle size={12} /> Reviewed
                    </span>
                  ) : (
                    <span className={`risk-badge ${level}`}>{level}</span>
                  )}
                </td>
                <td onClick={e => e.stopPropagation()}>
                  <button
                    className="btn-ghost"
                    style={{ padding: '4px 8px', fontSize: 11 }}
                    onClick={() => onSelect(alert)}
                  >
                    <Eye size={12} /> Explain
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {filtered.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--text-muted)', fontSize: 13 }}>
          No alerts match the current filter
        </div>
      )}
    </div>
  );
}
