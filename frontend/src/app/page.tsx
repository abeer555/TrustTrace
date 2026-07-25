'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Activity, BellRing, ShieldAlert, Users, RefreshCw, Zap,
} from 'lucide-react';
import StatsCard from '@/components/StatsCard';
import TimelineChart from '@/components/TimelineChart';
import AnomalyDonut from '@/components/AnomalyDonut';
import AnomalyBadge from '@/components/AnomalyBadge';
import RiskGauge from '@/components/RiskGauge';
import {
  getDashboardStats, getTimeline, getAnomalyDistribution, getTopEntities, runSimulation
} from '@/lib/api';
import type { DashboardStats, TimelinePoint, TopEntity } from '@/lib/types';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [distribution, setDistribution] = useState<Record<string, number>>({});
  const [topEntities, setTopEntities] = useState<TopEntity[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchAll = useCallback(async () => {
    try {
      const [s, t, d, e] = await Promise.all([
        getDashboardStats(),
        getTimeline(48),
        getAnomalyDistribution(),
        getTopEntities(8),
      ]);
      setStats(s);
      setTimeline(t);
      setDistribution(d);
      setTopEntities(e);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const res = await runSimulation();
      alert(`✅ Simulated ${res.events_simulated} events successfully!`);
      await fetchAll();
    } catch (err) {
      alert('Simulation failed — ensure the backend is running and models are trained.');
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="animate-fade-up">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Security Overview</h1>
          <p className="page-subtitle">
            Real-time behavioral anomaly detection {mounted ? `· Last updated ${lastRefresh.toLocaleTimeString()}` : ''}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn-ghost" onClick={fetchAll} disabled={loading}>
            <RefreshCw size={13} className={loading ? 'animate-spin-slow' : ''} />
            Refresh
          </button>
          <button className="btn-primary" onClick={handleSimulate} disabled={simulating}>
            <Zap size={13} />
            {simulating ? 'Simulating…' : 'Run Simulation'}
          </button>
        </div>
      </div>

      {/* Stats cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatsCard
          title="Total Events"
          value={loading ? '—' : (stats?.total_events ?? 0).toLocaleString()}
          subtitle="Access events processed"
          icon={Activity}
          accent="cyan"
          loading={loading}
        />
        <StatsCard
          title="Total Alerts"
          value={loading ? '—' : (stats?.total_alerts ?? 0).toLocaleString()}
          subtitle={loading ? '' : `${((stats?.alert_rate ?? 0) * 100).toFixed(2)}% alert rate`}
          icon={BellRing}
          accent="red"
          loading={loading}
        />
        <StatsCard
          title="High-Risk Entities"
          value={loading ? '—' : (stats?.high_risk_entities ?? 0).toLocaleString()}
          subtitle="Score > 0.70"
          icon={ShieldAlert}
          accent="purple"
          loading={loading}
        />
        <StatsCard
          title="Anomaly Types"
          value={loading ? '—' : Object.keys(distribution).filter(k => k !== 'normal').length}
          subtitle="Distinct attack categories"
          icon={Users}
          accent="green"
          loading={loading}
        />
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        <div className="glass-card" style={{ padding: '20px 24px' }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Event & Alert Timeline
          </h2>
          <TimelineChart data={timeline} loading={loading} />
        </div>
        <div className="glass-card" style={{ padding: '20px 24px' }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Anomaly Distribution
          </h2>
          <AnomalyDonut data={distribution} loading={loading} />
        </div>
      </div>

      {/* Top risk entities */}
      <div className="glass-card" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>
            Top Risk Entities
          </h2>
          <Link href="/entities" style={{ fontSize: 12, color: 'var(--accent-cyan)', textDecoration: 'none' }}>
            View all →
          </Link>
        </div>

        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 52, borderRadius: 8 }} />
            ))}
          </div>
        ) : topEntities.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 0', color: 'var(--text-muted)', fontSize: 13 }}>
            No alerts yet — click <strong>Run Simulation</strong> to populate data
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {topEntities.map((entity, i) => (
              <Link
                key={entity.entity_id}
                href={`/entities/${encodeURIComponent(entity.entity_id)}`}
                style={{ textDecoration: 'none' }}
              >
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 16,
                  background: 'var(--bg-panel)',
                  border: '1px solid var(--border)',
                  borderRadius: 8, padding: '10px 16px',
                  cursor: 'pointer', transition: 'background 0.15s',
                }}>
                  {/* Rank */}
                  <span style={{ fontSize: 11, fontWeight: 700, color: i < 3 ? '#f59e0b' : 'var(--text-muted)', width: 16, textAlign: 'center' }}>
                    #{i + 1}
                  </span>

                  {/* Gauge */}
                  <RiskGauge score={entity.max_risk_score} size={40} showLabel={false} />

                  {/* Entity info */}
                  <div style={{ flex: 1 }}>
                    <span className="entity-pill">{entity.entity_id}</span>
                    <div style={{ marginTop: 4 }}>
                      <AnomalyBadge type={entity.latest_anomaly_type} size="sm" />
                    </div>
                  </div>

                  {/* Alert count */}
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>
                      {entity.alert_count}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>alerts</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Hour heatmap */}
      {!loading && stats && stats.events_by_hour.length > 0 && (
        <div className="glass-card" style={{ padding: '20px 24px', marginTop: 16 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Activity by Hour
          </h2>
          <div style={{ display: 'flex', gap: 4, flexWrap: 'nowrap', alignItems: 'flex-end' }}>
            {Array.from({ length: 24 }).map((_, h) => {
              const bucket = stats.events_by_hour.find(b => b.hour === h);
              const count = bucket?.events ?? 0;
              const maxCount = Math.max(...stats.events_by_hour.map(b => b.events), 1);
              const alertCount = bucket?.alerts ?? 0;
              const heightPct = count / maxCount;
              const barColor = alertCount > 0 ? '#ef4444' : '#00d4ff';
              return (
                <div key={h} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div
                    title={`${h}:00 — ${count} events, ${alertCount} alerts`}
                    className="heatmap-cell"
                    style={{
                      width: '100%', height: 60 * heightPct + 4,
                      background: `${barColor}${Math.round(0.3 + heightPct * 0.7 * 255).toString(16).padStart(2, '0')}`,
                      border: `1px solid ${barColor}33`,
                      borderRadius: 4,
                    }}
                  />
                  <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>{h}</span>
                </div>
              );
            })}
          </div>
          <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 8 }}>
            <span style={{ color: '#00d4ff' }}>■</span> Events &nbsp;
            <span style={{ color: '#ef4444' }}>■</span> Hours with alerts
          </p>
        </div>
      )}
    </div>
  );
}
