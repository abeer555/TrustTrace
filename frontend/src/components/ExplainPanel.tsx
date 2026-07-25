'use client';

import { useEffect, useState } from 'react';
import { X, CheckCircle, ExternalLink, AlertTriangle, Info } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import type { AlertDetail } from '@/lib/types';
import { getAlertDetail, reviewAlert } from '@/lib/api';
import AnomalyBadge from './AnomalyBadge';
import RiskGauge from './RiskGauge';
import { getAnomalyColor } from '@/lib/utils';

interface ExplainPanelProps {
  alertId: number | null;
  onClose: () => void;
  onReviewed?: (id: number) => void;
}

export default function ExplainPanel({ alertId, onClose, onReviewed }: ExplainPanelProps) {
  const [detail, setDetail] = useState<AlertDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [marking, setMarking] = useState(false);

  useEffect(() => {
    if (!alertId) return;
    setLoading(true);
    setDetail(null);
    getAlertDetail(alertId)
      .then(setDetail)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [alertId]);

  if (!alertId) return null;

  const handleReview = async () => {
    if (!detail) return;
    setMarking(true);
    try {
      await reviewAlert(detail.id);
      setDetail(d => d ? { ...d, is_reviewed: true } : d);
      onReviewed?.(detail.id);
    } finally {
      setMarking(false);
    }
  };

  const accentColor = detail ? getAnomalyColor(detail.anomaly_type) : '#00d4ff';

  return (
    <>
      {/* Overlay */}
      <div className="drawer-overlay" onClick={onClose} />

      {/* Drawer */}
      <div className="drawer animate-slide-in-right">
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>Alert Explanation</h2>
            {detail && (
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Alert #{detail.id} · {(() => { try { return format(parseISO(detail.timestamp), 'MMM d, HH:mm:ss'); } catch { return detail.timestamp; } })()}
              </p>
            )}
          </div>
          <button className="btn-ghost" onClick={onClose} style={{ padding: '6px' }}>
            <X size={16} />
          </button>
        </div>

        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 60, borderRadius: 8 }} />
            ))}
          </div>
        )}

        {detail && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Risk + type */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
              <RiskGauge score={detail.risk_score} size={88} />
              <div>
                <AnomalyBadge type={detail.anomaly_type} />
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 8 }}>
                  Entity: <span className="entity-pill" style={{ marginLeft: 4 }}>{detail.entity_id}</span>
                </p>
                {detail.is_reviewed && (
                  <p style={{ fontSize: 11, color: '#10b981', display: 'flex', alignItems: 'center', gap: 4, marginTop: 6 }}>
                    <CheckCircle size={12} /> Reviewed
                  </p>
                )}
              </div>
            </div>

            <hr className="tt-divider" />

            {/* Explanation factors */}
            <div>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 10 }}>
                Contributing Factors
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {detail.explanation_factors.map((f, i) => {
                  const contrib = f.contribution ?? 0;
                  const desc = f.description || f.desc || String(f);
                  return (
                    <div key={i} style={{
                      background: 'var(--bg-panel)',
                      border: `1px solid ${i === 0 ? accentColor + '44' : 'var(--border)'}`,
                      borderRadius: 8, padding: '10px 14px',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: contrib > 0 ? 6 : 0 }}>
                        <p style={{ fontSize: 12, color: 'var(--text-primary)', flex: 1 }}>{desc}</p>
                        {contrib > 0 && (
                          <span style={{ fontSize: 11, fontWeight: 700, color: accentColor, marginLeft: 8 }}>
                            +{(contrib * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                      {contrib > 0 && (
                        <div className="progress-bar">
                          <div className="progress-bar-fill" style={{ width: `${contrib * 100}%`, background: accentColor }} />
                        </div>
                      )}
                      {f.feature && f.feature !== 'unknown' && (
                        <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'JetBrains Mono, monospace' }}>
                          feature: {f.feature}{f.value !== undefined ? ` = ${f.value}` : ''}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <hr className="tt-divider" />

            {/* Event context */}
            <div>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 10 }}>
                Event Context
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                {[
                  ['Source IP', detail.entity_history_summary?.source_ip],
                  ['Auth Method', detail.entity_history_summary?.auth_method],
                  ['Resource', detail.entity_history_summary?.resource_accessed],
                  ['Session (min)', detail.entity_history_summary?.session_duration],
                  ['Total Events', detail.entity_history_summary?.total_events],
                  ['Total Alerts', detail.entity_history_summary?.total_alerts],
                ].map(([k, v]) => (
                  <div key={String(k)} style={{ background: 'var(--bg-panel)', borderRadius: 6, padding: '8px 10px', border: '1px solid var(--border)' }}>
                    <p style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{k}</p>
                    <p style={{ fontSize: 12, color: 'var(--text-primary)', fontWeight: 500, marginTop: 2, fontFamily: 'JetBrains Mono, monospace', wordBreak: 'break-all' }}>
                      {v ?? '—'}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <hr className="tt-divider" />

            {/* Actions */}
            <div style={{ display: 'flex', gap: 10 }}>
              {!detail.is_reviewed && (
                <button className="btn-primary" onClick={handleReview} disabled={marking} style={{ flex: 1 }}>
                  <CheckCircle size={14} />
                  {marking ? 'Marking…' : 'Mark Reviewed'}
                </button>
              )}
              <a
                href={`/entities/${encodeURIComponent(detail.entity_id)}`}
                className="btn-ghost"
                style={{ flex: 1, textDecoration: 'none', justifyContent: 'center' }}
              >
                <ExternalLink size={13} /> Entity Profile
              </a>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
