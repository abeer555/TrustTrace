// TypeScript interfaces matching backend Pydantic schemas

export interface AccessEvent {
  entity_id: string;
  entity_type: string;
  timestamp: string;
  source_ip: string;
  geo_location: string;
  resource_accessed: string;
  auth_method: string;
  session_duration: number;
  command_sequence: string[];
  device_fingerprint: Record<string, string>;
}

export interface RiskScoreResponse {
  event_id: number | null;
  entity_id: string;
  risk_score: number;
  anomaly_type: string;
  explanation: string[];
  is_cold_start: boolean;
}

export interface AlertItem {
  id: number;
  entity_id: string;
  risk_score: number;
  anomaly_type: string;
  top_factor: string;
  timestamp: string;
  is_reviewed: boolean;
}

export interface ExplanationFactor {
  feature?: string;
  value?: number | string;
  contribution?: number;
  description: string;
  desc?: string;
}

export interface AlertDetail extends AlertItem {
  explanation_factors: ExplanationFactor[];
  entity_history_summary: {
    total_events: number;
    total_alerts: number;
    source_ip: string;
    geo_location: string;
    resource_accessed: string;
    auth_method: string;
    session_duration: number;
    device_fingerprint: string;
  };
}

export interface EntityListItem {
  entity_id: string;
  entity_type: string;
  event_count: number;
  max_risk_score: number;
  alert_count: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface EntityProfile {
  entity_id: string;
  entity_type: string;
  event_count: number;
  risk_level: string;
  typical_hours: number[];
  typical_geos: string[];
  typical_resources: string[];
  recent_alerts: number;
}

export interface EntityEvent {
  id: number;
  timestamp: string;
  source_ip: string;
  geo_location: string;
  resource_accessed: string;
  auth_method: string;
  session_duration: number;
  risk_score: number;
  anomaly_type: string;
  raw_label: string;
}

export interface DashboardStats {
  total_events: number;
  total_alerts: number;
  alert_rate: number;
  high_risk_entities: number;
  anomaly_distribution: Record<string, number>;
  events_by_hour: Array<{ hour: number; events: number; alerts: number }>;
}

export interface TimelinePoint {
  timestamp: string;
  events: number;
  alerts: number;
}

export interface TopEntity {
  entity_id: string;
  alert_count: number;
  max_risk_score: number;
  latest_anomaly_type: string;
}

export type AnomalyType =
  | 'normal'
  | 'brute_force'
  | 'impossible_travel'
  | 'credential_stuffing'
  | 'lateral_movement'
  | 'device_spoofing'
  | 'low_and_slow'
  | 'insider_drift'
  | 'unknown';
