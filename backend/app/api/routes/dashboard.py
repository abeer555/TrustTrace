from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, distinct, text
from app.core.database import AsyncSessionLocal, Event, Alert, EntityProfileModel
from app.models.schemas import DashboardStats
from datetime import datetime, timedelta, timezone
import json

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    event_count = await db.scalar(select(func.count(Event.id))) or 0
    alert_count = await db.scalar(select(func.count(Alert.id))) or 0

    # High-risk entities: entities with any alert in last 7 days with score > 0.7
    high_risk = await db.scalar(
        select(func.count(distinct(Alert.entity_id))).where(Alert.risk_score > 0.7)
    ) or 0

    # Anomaly distribution
    stmt = select(Alert.anomaly_type, func.count(Alert.id)).group_by(Alert.anomaly_type)
    result = await db.execute(stmt)
    anomaly_dist = {row[0]: row[1] for row in result.all() if row[0]}

    # Events by hour (last 24h)
    events_by_hour = []
    try:
        stmt_hour = select(
            func.strftime('%H', Event.timestamp).label('hour'),
            func.count(Event.id).label('count'),
            func.count(Alert.id).label('alerts')
        ).outerjoin(Alert, Alert.event_id == Event.id).group_by('hour').order_by('hour')
        result_hour = await db.execute(stmt_hour)
        for row in result_hour.all():
            events_by_hour.append({
                "hour": int(row[0]) if row[0] else 0,
                "events": row[1],
                "alerts": row[2] or 0
            })
    except Exception:
        events_by_hour = [{"hour": h, "events": 0, "alerts": 0} for h in range(24)]

    return DashboardStats(
        total_events=event_count,
        total_alerts=alert_count,
        alert_rate=(alert_count / event_count) if event_count > 0 else 0,
        high_risk_entities=high_risk,
        anomaly_distribution=anomaly_dist,
        events_by_hour=events_by_hour
    )

@router.get("/dashboard/timeline")
async def get_timeline(hours: int = Query(24, ge=1, le=168), db: AsyncSession = Depends(get_db)):
    """Return event and alert counts grouped by hour for the last N hours."""
    try:
        stmt = select(
            func.strftime('%Y-%m-%dT%H:00:00', Event.timestamp).label('bucket'),
            func.count(Event.id).label('event_count')
        ).group_by('bucket').order_by('bucket')
        result = await db.execute(stmt)
        rows = result.all()

        stmt_a = select(
            func.strftime('%Y-%m-%dT%H:00:00', Alert.created_at).label('bucket'),
            func.count(Alert.id).label('alert_count')
        ).group_by('bucket').order_by('bucket')
        result_a = await db.execute(stmt_a)
        alert_rows = {row[0]: row[1] for row in result_a.all()}

        return [
            {
                "timestamp": row[0],
                "events": row[1],
                "alerts": alert_rows.get(row[0], 0)
            }
            for row in rows
        ]
    except Exception:
        return []

@router.get("/dashboard/anomaly-distribution")
async def get_anomaly_distribution(db: AsyncSession = Depends(get_db)):
    stmt = select(Alert.anomaly_type, func.count(Alert.id)).group_by(Alert.anomaly_type)
    result = await db.execute(stmt)
    return {row[0]: row[1] for row in result.all() if row[0]}

@router.get("/dashboard/top-entities")
async def get_top_entities(limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    """Top entities by number of alerts."""
    stmt = select(
        Alert.entity_id,
        func.count(Alert.id).label('alert_count'),
        func.max(Alert.risk_score).label('max_risk_score'),
        func.max(Alert.anomaly_type).label('latest_type')
    ).group_by(Alert.entity_id).order_by(func.count(Alert.id).desc()).limit(limit)
    result = await db.execute(stmt)
    return [
        {
            "entity_id": row[0],
            "alert_count": row[1],
            "max_risk_score": round(row[2], 3),
            "latest_anomaly_type": row[3]
        }
        for row in result.all()
    ]
