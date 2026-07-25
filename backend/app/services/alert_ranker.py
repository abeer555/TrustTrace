from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.core.database import Alert, Event
from app.models.schemas import AlertItem

class AlertRanker:
    async def get_top_alerts(self, db: AsyncSession, n: int = 100, min_score: float = 0.5) -> list[AlertItem]:
        stmt = select(Alert, Event).join(Event, Alert.event_id == Event.id).where(Alert.risk_score >= min_score).order_by(desc(Alert.risk_score)).limit(n)
        result = await db.execute(stmt)
        rows = result.all()
        
        items = []
        for alert, event in rows:
            items.append(AlertItem(
                id=alert.id,
                entity_id=alert.entity_id,
                risk_score=alert.risk_score,
                anomaly_type=alert.anomaly_type,
                top_factor="Multiple factors", # Simplify for now
                timestamp=event.timestamp,
                is_reviewed=alert.is_reviewed
            ))
        return items
        
    async def compute_alert_budget_threshold(self, db: AsyncSession, total_events: int, budget_pct: float = 0.01) -> float:
        # Simplistic implementation
        stmt = select(Alert.risk_score).order_by(desc(Alert.risk_score)).limit(max(1, int(total_events * budget_pct)))
        result = await db.execute(stmt)
        scores = result.scalars().all()
        if not scores:
            return 0.5
        return scores[-1]
