from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func
from app.core.database import AsyncSessionLocal, Alert, Event
from app.models.schemas import AlertItem, AlertDetail
import json

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def _extract_top_factor(explanation_json: str) -> str:
    """Parse explanation JSON and return the most impactful factor description."""
    try:
        factors = json.loads(explanation_json)
        if isinstance(factors, list) and factors:
            first = factors[0]
            if isinstance(first, dict):
                return first.get("description", first.get("desc", str(first)))
            return str(first)
    except Exception:
        pass
    return "Anomalous activity detected"

@router.get("/alerts", response_model=list[AlertItem])
async def get_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    anomaly_type: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Alert, Event).join(Event, Alert.event_id == Event.id)
    if min_score > 0:
        stmt = stmt.where(Alert.risk_score >= min_score)
    if anomaly_type:
        stmt = stmt.where(Alert.anomaly_type == anomaly_type)

    stmt = stmt.order_by(desc(Alert.risk_score)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)

    items = []
    for alert, event in result.all():
        items.append(AlertItem(
            id=alert.id,
            entity_id=alert.entity_id,
            risk_score=round(alert.risk_score, 4),
            anomaly_type=alert.anomaly_type or "unknown",
            top_factor=_extract_top_factor(alert.explanation_json),
            timestamp=event.timestamp,
            is_reviewed=alert.is_reviewed
        ))
    return items

@router.get("/alerts/count")
async def count_alerts(
    min_score: float = Query(0.0),
    anomaly_type: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(func.count(Alert.id))
    if min_score > 0:
        stmt = stmt.where(Alert.risk_score >= min_score)
    if anomaly_type:
        stmt = stmt.where(Alert.anomaly_type == anomaly_type)
    count = await db.scalar(stmt) or 0
    return {"count": count}

@router.get("/alerts/{alert_id}", response_model=AlertDetail)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Alert, Event).join(Event, Alert.event_id == Event.id).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert, event = row

    # Parse explanation factors
    try:
        raw = json.loads(alert.explanation_json)
        if isinstance(raw, list):
            factors = []
            for item in raw:
                if isinstance(item, dict):
                    factors.append(item)
                else:
                    factors.append({"description": str(item), "contribution": 0.0, "feature": "unknown"})
        else:
            factors = [{"description": str(raw), "contribution": 0.0, "feature": "unknown"}]
    except Exception:
        factors = [{"description": "Anomalous activity detected", "contribution": 1.0, "feature": "ensemble"}]

    # Build entity history summary
    entity_stmt = select(
        func.count(Event.id).label("total_events"),
        func.count(Alert.id).label("total_alerts")
    ).outerjoin(Alert, Alert.event_id == Event.id).where(Event.entity_id == alert.entity_id)
    entity_result = await db.execute(entity_stmt)
    entity_row = entity_result.first()

    return AlertDetail(
        id=alert.id,
        entity_id=alert.entity_id,
        risk_score=round(alert.risk_score, 4),
        anomaly_type=alert.anomaly_type or "unknown",
        top_factor=_extract_top_factor(alert.explanation_json),
        timestamp=event.timestamp,
        is_reviewed=alert.is_reviewed,
        explanation_factors=factors,
        entity_history_summary={
            "total_events": entity_row[0] if entity_row else 0,
            "total_alerts": entity_row[1] if entity_row else 0,
            "source_ip": event.source_ip,
            "geo_location": event.geo_location,
            "resource_accessed": event.resource_accessed,
            "auth_method": event.auth_method,
            "session_duration": event.session_duration,
            "device_fingerprint": event.device_fingerprint,
        }
    )

@router.patch("/alerts/{alert_id}/review")
async def review_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_reviewed = True
    await db.commit()
    return {"status": "success", "alert_id": alert_id}
