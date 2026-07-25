from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from app.core.database import AsyncSessionLocal, Event, Alert
from app.models.schemas import EntityProfile
from collections import Counter
import json

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/entities")
async def get_entities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    entity_type: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(
        Event.entity_id,
        Event.entity_type,
        func.count(Event.id).label("event_count"),
        func.max(Event.risk_score).label("max_risk"),
        func.count(Alert.id).label("alert_count")
    ).outerjoin(Alert, Alert.event_id == Event.id)

    if entity_type:
        stmt = stmt.where(Event.entity_type == entity_type)

    stmt = stmt.group_by(Event.entity_id, Event.entity_type)\
               .order_by(desc(func.max(Event.risk_score)))\
               .offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "entity_id": row[0],
            "entity_type": row[1],
            "event_count": row[2],
            "max_risk_score": round(row[3] or 0.0, 4),
            "alert_count": row[4],
            "risk_level": "critical" if (row[3] or 0) > 0.85 else
                          "high" if (row[3] or 0) > 0.7 else
                          "medium" if (row[3] or 0) > 0.5 else "low"
        }
        for row in rows
    ]

@router.get("/entities/count")
async def count_entities(db: AsyncSession = Depends(get_db)):
    count = await db.scalar(select(func.count(func.distinct(Event.entity_id)))) or 0
    return {"count": count}

@router.get("/entities/{entity_id}", response_model=EntityProfile)
async def get_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    # Fetch all events for entity
    stmt = select(Event).where(Event.entity_id == entity_id).order_by(Event.timestamp.desc()).limit(500)
    result = await db.execute(stmt)
    events = result.scalars().all()

    if not events:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Compute behavioral profile from events
    hours = []
    geos = []
    resources = []
    for e in events:
        hours.append(e.timestamp.hour)
        try:
            geo = json.loads(e.geo_location)
            geos.append(geo.get("city", "Unknown"))
        except Exception:
            geos.append("Unknown")
        resources.append(e.resource_accessed)

    # Most common hours (top 6)
    hour_counts = Counter(hours)
    typical_hours = [h for h, _ in hour_counts.most_common(6)]

    # Most common geos (top 3)
    geo_counts = Counter(geos)
    typical_geos = [g for g, _ in geo_counts.most_common(3)]

    # Most common resources (top 5)
    resource_counts = Counter(resources)
    typical_resources = [r for r, _ in resource_counts.most_common(5)]

    max_risk = max((e.risk_score or 0.0) for e in events)
    risk_level = "critical" if max_risk > 0.85 else "high" if max_risk > 0.7 else "medium" if max_risk > 0.5 else "low"
    recent_alerts = sum(1 for e in events if (e.risk_score or 0) > 0.5)

    return EntityProfile(
        entity_id=entity_id,
        entity_type=events[0].entity_type,
        event_count=len(events),
        risk_level=risk_level,
        typical_hours=sorted(typical_hours),
        typical_geos=typical_geos,
        typical_resources=typical_resources,
        recent_alerts=recent_alerts
    )

@router.get("/entities/{entity_id}/events")
async def get_entity_events(
    entity_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Event).where(Event.entity_id == entity_id).order_by(Event.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        {
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "source_ip": e.source_ip,
            "geo_location": e.geo_location,
            "resource_accessed": e.resource_accessed,
            "auth_method": e.auth_method,
            "session_duration": e.session_duration,
            "risk_score": round(e.risk_score or 0.0, 4),
            "anomaly_type": e.anomaly_type or "normal",
            "raw_label": e.raw_label
        }
        for e in events
    ]

@router.get("/entities/{entity_id}/alerts")
async def get_entity_alerts(
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Alert, Event).join(Event, Alert.event_id == Event.id)\
           .where(Alert.entity_id == entity_id)\
           .order_by(desc(Alert.risk_score)).limit(limit)
    result = await db.execute(stmt)

    alerts = []
    for alert, event in result.all():
        alerts.append({
            "id": alert.id,
            "risk_score": round(alert.risk_score, 4),
            "anomaly_type": alert.anomaly_type,
            "timestamp": event.timestamp.isoformat(),
            "is_reviewed": alert.is_reviewed
        })
    return alerts
