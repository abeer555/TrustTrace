from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "TrustTrace"
    DATA_DIR: str = str(BASE_DIR / "data")
    MODELS_DIR: str = str(BASE_DIR / "data" / "trained_models")
    GENERATED_DIR: str = str(BASE_DIR / "data" / "generated")
    DATABASE_URL: str = f"sqlite+aiosqlite:///{str(BASE_DIR / 'data' / 'trusetrace.db')}"
    TOP_ALERT_PERCENTILE: float = 0.01
    ANOMALY_THRESHOLD: float = 0.5
    MIN_HISTORY_FOR_PROFILE: int = 10

settings = Settings()
