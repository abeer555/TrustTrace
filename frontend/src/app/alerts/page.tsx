'use client';

import { useEffect, useState, useCallback } from 'react';
import { RefreshCw, Filter } from 'lucide-react';
import AlertTable from '@/components/AlertTable';
import ExplainPanel from '@/components/ExplainPanel';
import { getAlerts } from '@/lib/api';
import type { AlertItem } from '@/lib/types';
import { ANOMALY_LABELS } from '@/lib/utils';

const ANOMALY_OPTIONS = [
  '', 'brute_force', 'impossible_travel', 'credential_stuffing',
  'lateral_movement', 'device_spoofing', 'low_and_slow', 'insider_drift'
];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [minScore, setMinScore] = useState(0);
  const [anomalyType, setAnomalyType] = useState('');
  const [page, setPage] = useState(1);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAlerts({
        page,
        page_size: 100,
        min_score: minScore,
        anomaly_type: anomalyType || undefined,
      });
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, minScore, anomalyType]);

  useEffect(() => { fetchAlerts(); }, [fetchAlerts]);

  const handleReviewed = (id: number) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, is_reviewed: true } : a));
  };

  return (
    <div className="animate-fade-up">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Alert Queue</h1>
          <p className="page-subtitle">
            Ranked by risk score · {alerts.length} alert{alerts.length !== 1 ? 's' : ''} loaded
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          {/* Min score filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Min Risk</label>
            <select
              className="tt-select"
              value={minScore}
              onChange={e => { setMinScore(Number(e.target.value)); setPage(1); }}
            >
              <option value={0}>Any</option>
              <option value={0.5}>≥ 50%</option>
              <option value={0.7}>≥ 70%</option>
              <option value={0.85}>≥ 85% (Critical)</option>
            </select>
          </div>

          {/* Type filter */}
          <select
            className="tt-select"
            value={anomalyType}
            onChange={e => { setAnomalyType(e.target.value); setPage(1); }}
          >
            <option value="">All Types</option>
            {ANOMALY_OPTIONS.filter(Boolean).map(t => (
              <option key={t} value={t}>{ANOMALY_LABELS[t] || t}</option>
            ))}
          </select>

          <button className="btn-ghost" onClick={fetchAlerts} disabled={loading}>
            <RefreshCw size={13} className={loading ? 'animate-spin-slow' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Top-1% banner */}
      {alerts.length > 0 && (
        <div style={{
          background: 'rgba(239,68,68,0.08)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 8, padding: '10px 16px',
          marginBottom: 16,
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ef4444', boxShadow: '0 0 8px #ef4444' }} className="animate-pulse-glow" />
          <p style={{ fontSize: 12, color: '#fca5a5' }}>
            Top-1% alert budget threshold: showing highest-risk events first.
            <strong style={{ marginLeft: 4 }}>
              {Math.ceil(alerts.length * 0.01)} critical alert{Math.ceil(alerts.length * 0.01) !== 1 ? 's' : ''}
            </strong> in top 1%.
          </p>
        </div>
      )}

      {/* Table */}
      <div className="glass-card" style={{ padding: '20px 24px' }}>
        <AlertTable
          alerts={alerts}
          loading={loading}
          onSelect={a => setSelectedId(a.id)}
          onReview={handleReviewed}
        />
      </div>

      {/* Explain drawer */}
      <ExplainPanel
        alertId={selectedId}
        onClose={() => setSelectedId(null)}
        onReviewed={handleReviewed}
      />
    </div>
  );
}
