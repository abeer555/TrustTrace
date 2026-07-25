from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, Event, Alert
from app.models.schemas import AccessEvent, RiskScoreResponse
from app.services.pipeline import pipeline
from app.core.config import settings
from app.ml.data_generator import SyntheticDataGenerator
import pandas as pd
from datetime import datetime, timezone
import json

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/ingest", response_model=RiskScoreResponse)
async def ingest_event(event: AccessEvent, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    try:
        response = pipeline.process_event(event)
        
        db_event = Event(
            entity_id=event.entity_id,
            entity_type=event.entity_type,
            timestamp=event.timestamp.replace(tzinfo=None) if event.timestamp.tzinfo else event.timestamp,
            source_ip=event.source_ip,
            geo_location=event.geo_location,
            resource_accessed=event.resource_accessed,
            auth_method=event.auth_method,
            session_duration=event.session_duration,
            command_sequence=json.dumps(event.command_sequence),
            device_fingerprint=json.dumps(event.device_fingerprint),
            risk_score=response.risk_score,
            anomaly_type=response.anomaly_type,
            explanation=json.dumps(response.explanation)
        )
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        
        response.event_id = db_event.id
        
        if response.risk_score > settings.ANOMALY_THRESHOLD:
            db_alert = Alert(
                event_id=db_event.id,
                entity_id=db_event.entity_id,
                risk_score=response.risk_score,
                anomaly_type=response.anomaly_type,
                explanation_json=json.dumps(response.explanation)
            )
            db.add(db_alert)
            await db.commit()
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
async def simulate_events(db: AsyncSession = Depends(get_db)):
    generator = SyntheticDataGenerator()
    df, profiles = generator.generate_dataset(n_days=1, attack_rate=0.05)

    EXPLANATIONS = {
        "brute_force": [
            {"feature": "n_failed_auths_last_1h", "description": "High failed authentication attempts in past hour (brute force pattern)", "contribution": 0.65},
            {"feature": "n_events_last_1h", "description": "Unusually high event frequency from single source IP", "contribution": 0.25},
        ],
        "impossible_travel": [
            {"feature": "geo_velocity", "description": "Login from geographically distant location within implausible time window", "contribution": 0.78},
            {"feature": "geo_location", "description": "Origin geo deviates significantly from entity home location", "contribution": 0.18},
        ],
        "credential_stuffing": [
            {"feature": "n_failed_auths_last_1h", "description": "Multiple account login failures from shared source IP range", "contribution": 0.55},
            {"feature": "n_events_last_1h", "description": "Coordinated login attempts across many entity IDs", "contribution": 0.35},
        ],
        "lateral_movement": [
            {"feature": "n_unique_resources_last_24h", "description": "Access to unusually broad set of resources - lateral movement indicator", "contribution": 0.70},
            {"feature": "resource_hash", "description": "Resources accessed never previously touched by this entity", "contribution": 0.22},
        ],
        "device_spoofing": [
            {"feature": "device_os_encoded", "description": "Device fingerprint (OS/MAC) mismatches historical profile for this entity", "contribution": 0.80},
            {"feature": "auth_method_encoded", "description": "Authentication method changed from entity baseline", "contribution": 0.15},
        ],
        "low_and_slow": [
            {"feature": "is_business_hours", "description": "Sensitive resource access occurring outside business hours", "contribution": 0.45},
            {"feature": "resource_hash", "description": "Gradual access to restricted resources not in entity normal footprint", "contribution": 0.42},
        ],
        "insider_drift": [
            {"feature": "n_unique_resources_last_24h", "description": "Gradually expanding resource access footprint over time", "contribution": 0.55},
            {"feature": "days_since_first_seen", "description": "Privilege escalation pattern detected relative to entity baseline", "contribution": 0.30},
        ],
        "normal": [
            {"feature": "ensemble_score", "description": "Ensemble anomaly score marginally above threshold - possible false positive", "contribution": 0.45},
            {"feature": "geo_velocity", "description": "Minor behavioral deviation from entity normal profile", "contribution": 0.30},
        ],
    }

    try:
        results_df = pipeline.batch_process(df)

        for _, row in results_df.iterrows():
            event_obj = Event(
                entity_id=row['entity_id'],
                entity_type=row['entity_type'],
                timestamp=pd.to_datetime(row['timestamp']).replace(tzinfo=None),
                source_ip=row['source_ip'],
                geo_location=row['geo_location'],
                resource_accessed=row['resource_accessed'],
                auth_method=row['auth_method'],
                session_duration=row['session_duration'],
                command_sequence=json.dumps(row['command_sequence']),
                device_fingerprint=row['device_fingerprint'],
                raw_label=row.get('label', 'normal'),
                risk_score=row['risk_score'],
                anomaly_type=row['anomaly_type']
            )
            db.add(event_obj)
            await db.commit()
            await db.refresh(event_obj)

            if row['risk_score'] > settings.ANOMALY_THRESHOLD:
                atype = row['anomaly_type'] or 'normal'
                explanation = EXPLANATIONS.get(atype, EXPLANATIONS['normal'])
                alert_obj = Alert(
                    event_id=event_obj.id,
                    entity_id=event_obj.entity_id,
                    risk_score=row['risk_score'],
                    anomaly_type=atype,
                    explanation_json=json.dumps(explanation)
                )
                db.add(alert_obj)
                await db.commit()

        return {"status": "success", "events_simulated": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

