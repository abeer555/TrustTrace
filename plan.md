# TrustTrace — Build Plan

> **Project**: AI-Powered Behavioral Anomaly Detection for Cybersecurity  
> **Stack**: Python (FastAPI + scikit-learn + SHAP) + Next.js 14 (TypeScript + Tailwind + Recharts)  
> **Goal**: End-to-end system: data generator → ML pipeline → REST API → analyst dashboard

---

## Status Legend
- `✅ DONE` — Complete
- `🔄 IN PROGRESS` — Currently being built
- `⬜ TODO` — Not started yet

---

## Phase 1 — Project Scaffold & Infrastructure ✅

| # | Task | Status |
|---|------|--------|
| 1.1 | Create `backend/` directory structure | ✅ |
| 1.2 | Create `frontend/` via `create-next-app` (Next.js 14 + TypeScript + Tailwind) | ✅ |
| 1.3 | Install frontend packages (recharts, framer-motion, lucide-react, axios, date-fns) | ✅ |
| 1.4 | Write `backend/requirements.txt` | ✅ |
| 1.5 | Install backend Python dependencies | ✅ |

---

## Phase 2 — Backend: Core Infrastructure ✅

| # | Task | Status |
|---|------|--------|
| 2.1 | `app/core/config.py` — Pydantic settings | ✅ |
| 2.2 | `app/core/database.py` — SQLAlchemy async, 3 tables (events, alerts, entity_profiles) | ✅ |
| 2.3 | `app/models/schemas.py` — Pydantic v2 models | ✅ |
| 2.4 | `app/main.py` — FastAPI app with CORS, lifespan, router registration | ✅ |

---

## Phase 3 — Backend: ML Pipeline ✅

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | `data_generator.py` — Synthetic access log generator | ✅ | 8 attack patterns, 350 entities |
| 3.2 | `feature_engineering.py` — Haversine geo velocity, rolling windows, label encoding | ✅ | Fixed pandas 2.x compat |
| 3.3 | `baseline_profiler.py` — Per-entity EMA profiler with concept drift | ✅ |
| 3.4 | `anomaly_detector.py` — Isolation Forest + ensemble scorer | ✅ |
| 3.5 | `classifier.py` — Random Forest + adaptive SMOTE, 8-class | ✅ |
| 3.6 | `explainer.py` — SHAP + rule-based explanations | ✅ |
| 3.7 | `cold_start.py` — Population baseline for new entities | ✅ |
| 3.8 | `pipeline.py` — End-to-end inference pipeline | ✅ |
| 3.9 | `alert_ranker.py` — Top-1% alert budget | ✅ |
| 3.10 | `scripts/generate_data.py` — CLI data generation | ✅ |
| 3.11 | `scripts/train_models.py` — Training + evaluation script | ✅ |

---

## Phase 4 — Backend: API Routes ✅

| # | Task | Status |
|---|------|--------|
| 4.1 | `routes/ingest.py` — POST /ingest, POST /simulate (with proper explanations) | ✅ |
| 4.2 | `routes/alerts.py` — GET /alerts, GET /alerts/{id}, PATCH /review, GET /alerts/count | ✅ |
| 4.3 | `routes/entities.py` — GET /entities, GET /entities/{id}, /events, /alerts | ✅ |
| 4.4 | `routes/dashboard.py` — Stats, timeline, anomaly dist, top entities | ✅ |

---

## Phase 5 — Data Generation & Model Training ✅

| # | Task | Status | Result |
|---|------|--------|--------|
| 5.1 | Run `generate_data.py` | ✅ | 23,496 events (30 days, 350 entities) |
| 5.2 | Run `train_models.py` | ✅ | Models saved to `data/trained_models/` |
| 5.3 | Evaluate metrics | ✅ | AUC-ROC: **0.917**, Accuracy: **99%**, Brute Force F1: **0.94**, Lateral Movement F1: **1.00** |
| 5.4 | Start API server `uvicorn app.main:app --port 8000` | ✅ | Running on http://localhost:8000 |
| 5.5 | Run POST `/api/v1/simulate` × 2 to populate DB | ✅ | 1490 events, ~14 alerts in DB |

---

## Phase 6 — Frontend: Design System & Layout ✅

| # | Task | Status |
|---|------|--------|
| 6.1 | `globals.css` — Dark cybersecurity theme (navy/teal/red), glassmorphism, animations | ✅ |
| 6.2 | `layout.tsx` — Root layout with sidebar nav | ✅ |
| 6.3 | `lib/api.ts` — Typed Axios client for all endpoints | ✅ |
| 6.4 | `lib/types.ts` — TypeScript interfaces | ✅ |
| 6.5 | `lib/utils.ts` — Anomaly colors, risk levels, formatters | ✅ |

---

## Phase 7 — Frontend: Components ✅

| # | Component | Status |
|---|-----------|--------|
| 7.1 | `Sidebar` — Navigation with animated active states + system status indicator | ✅ |
| 7.2 | `StatsCard` — Metric card with accent top border, icon, value, trend | ✅ |
| 7.3 | `AnomalyBadge` — Color-coded attack type badge | ✅ |
| 7.4 | `RiskGauge` — SVG circular gauge with animated fill | ✅ |
| 7.5 | `TimelineChart` — Recharts AreaChart with gradient fills | ✅ |
| 7.6 | `AnomalyDonut` — Recharts donut chart for type distribution | ✅ |
| 7.7 | `AlertTable` — Filterable ranked table with risk gauge per row | ✅ |
| 7.8 | `ExplainPanel` — Slide-out drawer with SHAP factors + progress bars | ✅ |

---

## Phase 8 — Frontend: Pages ✅

| # | Page | Status |
|---|------|--------|
| 8.1 | `app/page.tsx` — Overview Dashboard (stats, timeline, donut, top entities, heatmap) | ✅ |
| 8.2 | `app/alerts/page.tsx` — Alert Queue (filters, top-1% banner, explain drawer) | ✅ |
| 8.3 | `app/entities/page.tsx` — Entity Browser (grid, risk summary, search) | ✅ |
| 8.4 | `app/entities/[id]/page.tsx` — Entity Deep-Dive (profile, event timeline, alerts) | ✅ |

---

## Phase 9 — Integration ✅

| # | Task | Status |
|---|------|--------|
| 9.1 | All pages connected to live backend API | ✅ |
| 9.2 | Loading skeletons, empty states on all pages | ✅ |
| 9.3 | Auto-refresh every 30s on dashboard | ✅ |
| 9.4 | Simulate button on dashboard | ✅ |
| 9.5 | Frontend running at http://localhost:3000 | ✅ |

---

## Phase 10 — Documentation ✅

| # | Task | Status |
|---|------|--------|
| 10.1 | `plan.md` — Build plan with status tracking | ✅ |
| 10.2 | `README.md` — Full project overview, quickstart, API ref, metrics | ✅ |

---

## Evaluation Results

| Metric | Value |
|--------|-------|
| Overall Accuracy | **99%** |
| Brute Force F1 | **0.94** |
| Lateral Movement F1 | **1.00** |
| Normal Class F1 | **1.00** |
| AUC-ROC (anomaly detection) | **0.917** |
| FPR at top-1% | Computed at threshold 0.380 |

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Anomaly scoring | Ensemble: IF (40%) + EMA profiler (40%) + rules (20%) | Balances global + entity-local + hard-coded signals |
| Class imbalance | Adaptive SMOTE + class_weight='balanced' | Prevents normal class from dominating; handles tiny minority classes |
| Concept drift | Exponential Moving Average profile update (α=0.1) | Adapts to legitimate behavior change |
| Cold start | Population-level group baseline per entity_type | Sensible defaults for new entities |
| Explainability | SHAP TreeExplainer + rule-based flags + NL synthesis | SOC-analyst-readable, not just scores |
| Feature engineering | Python-level rolling windows (not pandas rolling) | Pandas 2.x compatibility, works for string columns |
| Database | SQLite via SQLAlchemy async | Zero config, sufficient for demo |
| Frontend theme | Dark cybersecurity (navy/teal/red accent) + glassmorphism | Matches domain aesthetics |
