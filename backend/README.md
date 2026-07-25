# TrustTrace Backend

AI-powered behavioral anomaly detection system for cybersecurity.

## Setup

```bash
pip install -r requirements.txt
python scripts/generate_data.py
python scripts/train_models.py
uvicorn app.main:app --port 8000 --host 0.0.0.0
```

## API Endpoints

- POST /api/v1/ingest
- POST /api/v1/simulate
- GET /api/v1/alerts
- GET /api/v1/entities
- GET /api/v1/dashboard/stats
