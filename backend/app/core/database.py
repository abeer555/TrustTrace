import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Text, JSON
from datetime import datetime, timezone
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    entity_type: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    source_ip: Mapped[str] = mapped_column(String)
    geo_location: Mapped[str] = mapped_column(String)
    resource_accessed: Mapped[str] = mapped_column(String)
    auth_method: Mapped[str] = mapped_column(String)
    session_duration: Mapped[float] = mapped_column(Float)
    command_sequence: Mapped[str] = mapped_column(Text)
    device_fingerprint: Mapped[str] = mapped_column(Text)
    raw_label: Mapped[str] = mapped_column(String, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    anomaly_type: Mapped[str] = mapped_column(String, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(Integer)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    risk_score: Mapped[float] = mapped_column(Float)
    anomaly_type: Mapped[str] = mapped_column(String)
    explanation_json: Mapped[str] = mapped_column(Text)
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class EntityProfileModel(Base):
    __tablename__ = "entity_profiles"
    entity_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen: Mapped[datetime] = mapped_column(DateTime)
    last_seen: Mapped[datetime] = mapped_column(DateTime)
    profile_json: Mapped[str] = mapped_column(Text)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
