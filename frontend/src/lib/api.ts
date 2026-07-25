import axios from 'axios';
import type {
  AlertItem,
  AlertDetail,
  EntityListItem,
  EntityProfile,
  EntityEvent,
  DashboardStats,
  TimelinePoint,
  TopEntity,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// ── Dashboard ──────────────────────────────────────────────
export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await client.get('/dashboard/stats');
  return data;
}

export async function getTimeline(hours = 24): Promise<TimelinePoint[]> {
  const { data } = await client.get(`/dashboard/timeline?hours=${hours}`);
  return data;
}

export async function getAnomalyDistribution(): Promise<Record<string, number>> {
  const { data } = await client.get('/dashboard/anomaly-distribution');
  return data;
}

export async function getTopEntities(limit = 10): Promise<TopEntity[]> {
  const { data } = await client.get(`/dashboard/top-entities?limit=${limit}`);
  return data;
}

// ── Alerts ─────────────────────────────────────────────────
export async function getAlerts(params?: {
  page?: number;
  page_size?: number;
  min_score?: number;
  anomaly_type?: string;
}): Promise<AlertItem[]> {
  const { data } = await client.get('/alerts', { params });
  return data;
}

export async function getAlertCount(params?: {
  min_score?: number;
  anomaly_type?: string;
}): Promise<number> {
  const { data } = await client.get('/alerts/count', { params });
  return data.count;
}

export async function getAlertDetail(id: number): Promise<AlertDetail> {
  const { data } = await client.get(`/alerts/${id}`);
  return data;
}

export async function reviewAlert(id: number): Promise<void> {
  await client.patch(`/alerts/${id}/review`);
}

// ── Entities ───────────────────────────────────────────────
export async function getEntities(params?: {
  page?: number;
  page_size?: number;
  entity_type?: string;
}): Promise<EntityListItem[]> {
  const { data } = await client.get('/entities', { params });
  return data;
}

export async function getEntityProfile(entityId: string): Promise<EntityProfile> {
  const { data } = await client.get(`/entities/${encodeURIComponent(entityId)}`);
  return data;
}

export async function getEntityEvents(entityId: string, limit = 100): Promise<EntityEvent[]> {
  const { data } = await client.get(
    `/entities/${encodeURIComponent(entityId)}/events?limit=${limit}`
  );
  return data;
}

export async function getEntityAlerts(entityId: string, limit = 50): Promise<AlertItem[]> {
  const { data } = await client.get(
    `/entities/${encodeURIComponent(entityId)}/alerts?limit=${limit}`
  );
  return data;
}

// ── Simulation ─────────────────────────────────────────────
export async function runSimulation(): Promise<{ status: string; events_simulated: number }> {
  const { data } = await client.post('/simulate');
  return data;
}
