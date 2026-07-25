import type { AnomalyType } from './types';

export const ANOMALY_COLORS: Record<string, string> = {
  normal: '#10b981',
  brute_force: '#ef4444',
  impossible_travel: '#f97316',
  credential_stuffing: '#a855f7',
  lateral_movement: '#3b82f6',
  device_spoofing: '#eab308',
  low_and_slow: '#06b6d4',
  insider_drift: '#ec4899',
  unknown: '#6b7280',
};

export const ANOMALY_LABELS: Record<string, string> = {
  normal: 'Normal',
  brute_force: 'Brute Force',
  impossible_travel: 'Impossible Travel',
  credential_stuffing: 'Credential Stuffing',
  lateral_movement: 'Lateral Movement',
  device_spoofing: 'Device Spoofing',
  low_and_slow: 'Low & Slow',
  insider_drift: 'Insider Drift',
  unknown: 'Unknown',
};

export const RISK_COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#7c3aed',
};

export function getRiskLevel(score: number): 'low' | 'medium' | 'high' | 'critical' {
  if (score > 0.85) return 'critical';
  if (score > 0.7) return 'high';
  if (score > 0.5) return 'medium';
  return 'low';
}

export function getRiskColor(score: number): string {
  return RISK_COLORS[getRiskLevel(score)];
}

export function formatRiskScore(score: number): string {
  return (score * 100).toFixed(1) + '%';
}

export function formatEntityId(id: string): string {
  return id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export function getAnomalyColor(type: string): string {
  return ANOMALY_COLORS[type] || ANOMALY_COLORS.unknown;
}

export function getAnomalyLabel(type: string): string {
  return ANOMALY_LABELS[type] || type;
}
