from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AccessEvent(BaseModel):
    entity_id: str
    entity_type: str
    timestamp: datetime
    source_ip: str
    geo_location: str
    resource_accessed: str
    auth_method: str
    session_duration: float
    command_sequence: List[str]
    device_fingerprint: Dict[str, str]

class RiskScoreResponse(BaseModel):
    event_id: Optional[int] = None
    entity_id: str
    risk_score: float
    anomaly_type: str
    explanation: List[str]
    is_cold_start: bool

class AlertItem(BaseModel):
    id: int
    entity_id: str
    risk_score: float
    anomaly_type: str
    top_factor: str
    timestamp: datetime
    is_reviewed: bool

class AlertDetail(AlertItem):
    explanation_factors: List[Dict[str, Any]]
    entity_history_summary: Dict[str, Any]

class EntityProfile(BaseModel):
    entity_id: str
    entity_type: str
    event_count: int
    risk_level: str
    typical_hours: List[int]
    typical_geos: List[str]
    typical_resources: List[str]
    recent_alerts: int

class DashboardStats(BaseModel):
    total_events: int
    total_alerts: int
    alert_rate: float
    high_risk_entities: int
    anomaly_distribution: Dict[str, int]
    events_by_hour: List[Dict[str, Any]]
