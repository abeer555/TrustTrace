'use client';

import { useEffect, useState, useCallback } from 'react';
import { Search, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { getEntities } from '@/lib/api';
import type { EntityListItem } from '@/lib/types';
import AnomalyBadge from '@/components/AnomalyBadge';
import RiskGauge from '@/components/RiskGauge';

const RISK_LEVEL_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

export default function EntitiesPage() {
  const [entities, setEntities] = useState<EntityListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const fetchEntities = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getEntities({ page_size: 200, entity_type: typeFilter || undefined });
      setEntities(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [typeFilter]);

  useEffect(() => { fetchEntities(); }, [fetchEntities]);

  const filtered = entities
    .filter(e => !search || e.entity_id.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => (RISK_LEVEL_ORDER[a.risk_level] ?? 9) - (RISK_LEVEL_ORDER[b.risk_level] ?? 9));

  const riskCounts = {
    critical: filtered.filter(e => e.risk_level === 'critical').length,
    high: filtered.filter(e => e.risk_level === 'high').length,
    medium: filtered.filter(e => e.risk_level === 'medium').length,
    low: filtered.filter(e => e.risk_level === 'low').length,
  };

  return (
    <div className="animate-fade-up">
      <div className="page-header">
        <div>
          <h1 className="page-title">Entity Browser</h1>
          <p className="page-subtitle">{filtered.length} entities · sorted by risk level</p>
        </div>
        <button className="btn-ghost" onClick={fetchEntities} disabled={loading}>
          <RefreshCw size={13} className={loading ? 'animate-spin-slow' : ''} />
          Refresh
        </button>
      </div>

      {/* Risk summary pills */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        {[
          { level: 'critical', color: '#7c3aed', label: 'Critical' },
          { level: 'high', color: '#ef4444', label: 'High' },
          { level: 'medium', color: '#f59e0b', label: 'Medium' },
          { level: 'low', color: '#10b981', label: 'Low' },
        ].map(({ level, color, label }) => (
          <div key={level} style={{
            background: `${color}18`,
            border: `1px solid ${color}44`,
            borderRadius: 8, padding: '8px 16px',
            display: 'flex', flexDirection: 'column', alignItems: 'center',
          }}>
            <span style={{ fontSize: 22, fontWeight: 800, color }}>{riskCounts[level as keyof typeof riskCounts]}</span>
            <span style={{ fontSize: 10, color, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            className="tt-input" placeholder="Search entity ID…"
            value={search} onChange={e => setSearch(e.target.value)}
            style={{ width: '100%', paddingLeft: 30 }}
          />
        </div>
        <select className="tt-select" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="user">Users</option>
          <option value="service_account">Service Accounts</option>
          <option value="edge_device">Edge Devices</option>
        </select>
      </div>

      {/* Entity grid */}
      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 100, borderRadius: 10 }} />
          ))}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
          {filtered.map(entity => {
            const riskColors = { critical: '#7c3aed', high: '#ef4444', medium: '#f59e0b', low: '#10b981' };
            const color = riskColors[entity.risk_level] || '#6b7280';
            return (
              <Link key={entity.entity_id} href={`/entities/${encodeURIComponent(entity.entity_id)}`} style={{ textDecoration: 'none' }}>
                <div className="glass-card" style={{ padding: '16px 18px', cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <RiskGauge score={entity.max_risk_score} size={52} showLabel={false} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p className="entity-pill" style={{ fontSize: 11, marginBottom: 4, display: 'inline-flex' }}>
                        {entity.entity_id}
                      </p>
                      <p style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6 }}>
                        {entity.entity_type} · {entity.event_count} events
                      </p>
                      <span className={`risk-badge ${entity.risk_level}`}>
                        {entity.risk_level}
                      </span>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <p style={{ fontSize: 18, fontWeight: 800, color }}>{entity.alert_count}</p>
                      <p style={{ fontSize: 10, color: 'var(--text-muted)' }}>alerts</p>
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-muted)' }}>
          No entities found. Run a simulation first.
        </div>
      )}
    </div>
  );
}
