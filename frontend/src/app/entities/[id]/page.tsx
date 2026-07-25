'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Clock, MapPin, Server, Shield, Activity } from 'lucide-react';
import Link from 'next/link';
import { format, parseISO } from 'date-fns';
import { getEntityProfile, getEntityEvents, getEntityAlerts } from '@/lib/api';
import type { EntityProfile, EntityEvent } from '@/lib/types';
import type { AlertItem } from '@/lib/types';
import RiskGauge from '@/components/RiskGauge';
import AnomalyBadge from '@/components/AnomalyBadge';
import ExplainPanel from '@/components/ExplainPanel';
import { getRiskColor } from '@/lib/utils';

export default function EntityDetailPage() {
  const params = useParams();
  const entityId = decodeURIComponent(params.id as string);

  const [profile, setProfile] = useState<EntityProfile | null>(null);
  const [events, setEvents] = useState<EntityEvent[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlertId, setSelectedAlertId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'events' | 'alerts'>('events');

  useEffect(() => {
    if (!entityId) return;
    setLoading(true);
    Promise.all([
      getEntityProfile(entityId),
      getEntityEvents(entityId, 100),
      getEntityAlerts(entityId, 50),
    ]).then(([p, e, a]) => {
      setProfile(p);
      setEvents(e);
      setAlerts(a as unknown as AlertItem[]);
    }).catch(console.error)
      .finally(() => setLoading(false));
  }, [entityId]);

  if (loading) {
    return (
      <div className="animate-fade-up">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div className="skeleton" style={{ height: 120, borderRadius: 10 }} />
          <div className="skeleton" style={{ height: 300, borderRadius: 10 }} />
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-muted)' }}>
        Entity not found.{' '}
        <Link href="/entities" style={{ color: 'var(--accent-cyan)' }}>← Back</Link>
      </div>
    );
  }

  const maxRisk = events.reduce((m, e) => Math.max(m, e.risk_score), 0);
  const riskColor = getRiskColor(maxRisk);

  return (
    <div className="animate-fade-up">
      {/* Back */}
      <Link href="/entities" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-muted)', textDecoration: 'none', marginBottom: 20 }}>
        <ArrowLeft size={13} /> Back to Entities
      </Link>

      {/* Entity header */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <RiskGauge score={maxRisk} size={96} />
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span className="entity-pill" style={{ fontSize: 14 }}>{entityId}</span>
              <span className={`risk-badge ${profile.risk_level}`}>{profile.risk_level}</span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 12 }}>
              {profile.entity_type} · {profile.event_count} events total · {profile.recent_alerts} alerts
            </p>
            {/* Profile stats */}
            <div style={{ display: 'flex', gap: 20 }}>
              <div>
                <p style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Typical Hours</p>
                <p style={{ fontSize: 12, color: 'var(--text-primary)', marginTop: 2 }}>
                  {profile.typical_hours.length > 0
                    ? profile.typical_hours.map(h => `${h}:00`).join(', ')
                    : 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Home Geos</p>
                <p style={{ fontSize: 12, color: 'var(--text-primary)', marginTop: 2 }}>
                  {profile.typical_geos.join(', ') || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Top Resources</p>
                <p style={{ fontSize: 12, color: 'var(--text-primary)', marginTop: 2 }}>
                  {profile.typical_resources.slice(0, 2).join(', ') || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16 }}>
        {(['events', 'alerts'] as const).map(tab => (
          <button
            key={tab}
            className={activeTab === tab ? 'btn-primary' : 'btn-ghost'}
            onClick={() => setActiveTab(tab)}
            style={{ fontSize: 12 }}
          >
            {tab === 'events' ? <Activity size={12} /> : <Shield size={12} />}
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            <span style={{
              background: activeTab === tab ? 'rgba(255,255,255,0.2)' : 'var(--bg-elevated)',
              borderRadius: 10, padding: '1px 6px', fontSize: 10, fontWeight: 700,
            }}>
              {tab === 'events' ? events.length : alerts.length}
            </span>
          </button>
        ))}
      </div>

      {/* Events tab */}
      {activeTab === 'events' && (
        <div className="glass-card" style={{ padding: '20px 24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {events.map(ev => {
              const isAnomaly = ev.anomaly_type !== 'normal' && ev.risk_score > 0.5;
              return (
                <div key={ev.id} style={{
                  display: 'flex', alignItems: 'center', gap: 16,
                  background: isAnomaly ? 'rgba(239,68,68,0.05)' : 'var(--bg-panel)',
                  border: `1px solid ${isAnomaly ? 'rgba(239,68,68,0.25)' : 'var(--border)'}`,
                  borderRadius: 8, padding: '10px 14px',
                }}>
                  {/* Timeline dot */}
                  <div style={{
                    width: 10, height: 10, borderRadius: '50%', flexShrink: 0,
                    background: isAnomaly ? '#ef4444' : '#10b981',
                    boxShadow: isAnomaly ? '0 0 6px #ef4444' : 'none',
                  }} />
                  {/* Timestamp */}
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', minWidth: 120 }}>
                    {(() => { try { return format(parseISO(ev.timestamp), 'MMM d HH:mm:ss'); } catch { return ev.timestamp; } })()}
                  </span>
                  {/* Resource */}
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)', flex: 1, fontFamily: 'JetBrains Mono, monospace' }}>
                    {ev.resource_accessed}
                  </span>
                  {/* IP */}
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                    {ev.source_ip}
                  </span>
                  {/* Anomaly type */}
                  <AnomalyBadge type={ev.anomaly_type} size="sm" />
                  {/* Risk score */}
                  <span style={{ fontSize: 11, fontWeight: 700, color: getRiskColor(ev.risk_score), minWidth: 40, textAlign: 'right' }}>
                    {Math.round(ev.risk_score * 100)}%
                  </span>
                </div>
              );
            })}
            {events.length === 0 && (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 0', fontSize: 13 }}>No events found</p>
            )}
          </div>
        </div>
      )}

      {/* Alerts tab */}
      {activeTab === 'alerts' && (
        <div className="glass-card" style={{ padding: '20px 24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {alerts.map((alert: any) => (
              <div
                key={alert.id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 16,
                  background: 'var(--bg-panel)', border: '1px solid var(--border)',
                  borderRadius: 8, padding: '10px 14px', cursor: 'pointer',
                }}
                onClick={() => setSelectedAlertId(alert.id)}
              >
                <RiskGauge score={alert.risk_score} size={40} showLabel={false} />
                <AnomalyBadge type={alert.anomaly_type} />
                <span style={{ flex: 1, fontSize: 11, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                  {(() => { try { return format(parseISO(alert.timestamp), 'MMM d HH:mm:ss'); } catch { return alert.timestamp; } })()}
                </span>
                <button className="btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}>
                  Explain →
                </button>
              </div>
            ))}
            {alerts.length === 0 && (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 0', fontSize: 13 }}>No alerts for this entity</p>
            )}
          </div>
        </div>
      )}

      {/* Explain panel */}
      <ExplainPanel
        alertId={selectedAlertId}
        onClose={() => setSelectedAlertId(null)}
      />
    </div>
  );
}
