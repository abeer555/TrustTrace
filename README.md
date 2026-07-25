# TrustTrace 🛡️

**AI-Powered Behavioral Anomaly Detection for Cybersecurity**

TrustTrace detects intrusions, compromised credentials, and lateral movement in real-time by learning what *normal* looks like for every user, service account, and device — then flagging deviations with explainable risk scores.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     TrustTrace                          │
│                                                         │
│   Synthetic Data          ML Pipeline                   │
│   Generator          ┌────────────────────┐             │
│  (350 entities,      │ Isolation Forest   │             │
│   8 attack types)    │ + EMA Profiler     │ Ensemble    │
│        │             │ + Rule Engine      │ Score 0-1   │
│        ▼             └────────┬───────────┘             │
│   FastAPI Backend             │                         │
│   (SQLite + SQLAlchemy)       ▼                         │
│        │             RF Classifier                      │
│        │             (8 anomaly types)                  │
│        │                      │                         │
│        │             SHAP Explainer                     │
│        │             + Rule-Based NL                    │
│        ▼                      │                         │
│   Next.js Dashboard ◄─────────┘                         │
│   (Alerts · Entities · Charts)                          │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Generate 23k+ synthetic events (30 days, 350 entities, 8 attack types)
python scripts/generate_data.py

# Train models (IF + RF + SMOTE + SHAP) — prints evaluation metrics
python scripts/train_models.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 3. Populate Dashboard

Click **"Run Simulation"** on the dashboard, or:

```bash
curl -X POST http://localhost:8000/api/v1/simulate
```

---

## ML Pipeline

| Component | Approach | Purpose |
|-----------|----------|---------|
| **Baseline Profiler** | Per-entity EMA (α=0.1) | Concept drift adaptation |
| **Anomaly Detector** | Isolation Forest (n=200) | Global outlier scoring |
| **Ensemble Score** | IF(40%) + Profiler(40%) + Rules(20%) | Final risk score 0–1 |
| **Classifier** | Random Forest + SMOTE (8-class) | Attack type identification |
| **Explainer** | SHAP TreeExplainer + rule flags | Human-readable explanations |
| **Cold Start** | Population-level type baseline | New entity handling |

### Attack Taxonomy

| Type | Simulation | Key Signal |
|------|-----------|------------|
| `brute_force` | 10–30 rapid failed auths from one IP | `n_failed_auths_last_1h` |
| `impossible_travel` | Login from 5000+ km away in < 90 min | `geo_velocity` |
| `credential_stuffing` | Many entities, few IPs, high fail rate | `n_failed_auths_last_1h`, `n_events_last_1h` |
| `lateral_movement` | Rapid access to 20 novel resources | `n_unique_resources_last_24h` |
| `device_spoofing` | Mismatched OS/MAC vs history | `device_os_encoded` |
| `low_and_slow` | Off-hours, gradual, novel resources | `is_business_hours`, `resource_hash` |
| `insider_drift` | Slowly expanding resource footprint | `n_unique_resources_last_24h` |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingest` | Ingest single access event, return risk score |
| `POST` | `/api/v1/simulate` | Generate and process ~1000 events |
| `GET`  | `/api/v1/alerts` | Paginated, filterable alert queue |
| `GET`  | `/api/v1/alerts/{id}` | Alert detail + SHAP explanations |
| `PATCH`| `/api/v1/alerts/{id}/review` | Mark alert as reviewed |
| `GET`  | `/api/v1/entities` | Entity list with risk levels |
| `GET`  | `/api/v1/entities/{id}` | Entity profile + typical behavior |
| `GET`  | `/api/v1/entities/{id}/events` | Event history |
| `GET`  | `/api/v1/entities/{id}/alerts` | Entity alerts |
| `GET`  | `/api/v1/dashboard/stats` | Aggregate statistics |
| `GET`  | `/api/v1/dashboard/timeline` | Events/alerts over time |
| `GET`  | `/api/v1/dashboard/top-entities` | Highest-risk entities |

---

## Evaluation Results

*(From `train_models.py` on 4,700 held-out test events)*

| Metric | Value |
|--------|-------|
| Overall Accuracy | ~99% |
| Brute Force F1 | 0.94 |
| Lateral Movement F1 | 1.00 |
| Normal Class F1 | 1.00 |
| Anomaly Detection AUC-ROC | > 0.95 |

**Known Limitations:**
- `low_and_slow` and `device_spoofing` have low support in synthetic data (< 10 samples) — real-world performance would improve with more data
- Cold-start entities scored against population baseline — may have higher FPR
- SQLite not suitable for production scale; replace with PostgreSQL + streaming ingestion

---

## Deliverables Checklist

- [x] Synthetic data generator (8 attack patterns, 350 entities, 30 days)
- [x] Baseline profiling model (EMA per-entity + concept drift)
- [x] Detection model (Isolation Forest ensemble)
- [x] Anomaly classification (Random Forest + SMOTE, 8 classes)
- [x] Explainability layer (SHAP + rule-based natural language)
- [x] Analyst dashboard (Overview · Alert Queue · Entity Browser · Deep-Dive)
- [x] Cold-start handling (population-level type baselines)
- [x] Real-time ingestion API
