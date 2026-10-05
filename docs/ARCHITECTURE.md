# ARCHITECTURE.md — AirReady

Read `PROJECT_BRAIN.md` first if you haven't. This file explains how the three layers
(ML, Backend, Frontend) fit together and why they're split the way they are.

---

## 1. System diagram

```
┌─────────────────────┐
│   ml/ (offline)      │
│  ─────────────────   │
│  NASA C-MAPSS data    │
│       │                │
│       ▼                │
│  feature engineering   │
│       │                │
│       ▼                │
│  train RUL model       │
│       │                │
│       ▼                │
│  export: rul_model.pkl │──────┐
└─────────────────────┘      │
                               ▼
                    ┌─────────────────────┐
                    │  backend/ (FastAPI)  │
                    │  ─────────────────   │
                    │  loads rul_model.pkl │
                    │  + synthetic spares/  │
                    │    maintenance tables │
                    │       │                │
                    │       ▼                │
                    │  fleet readiness logic │
                    │       │                │
                    │       ▼                │
                    │  REST API (JSON)       │
                    └──────────┬───────────┘
                                │  HTTP (Axios)
                                ▼
                    ┌─────────────────────┐
                    │  frontend/ (React)    │
                    │  ─────────────────    │
                    │  Fleet Overview page   │
                    │  Engine Detail page    │
                    │  Alerts / Spares panel │
                    │  Baseline vs Predicted  │
                    │     comparison chart    │
                    └─────────────────────┘
```

---

## 2. Why three separate layers (and why it matters)

- **`ml/` is offline and batch.** It is not a live service. It reads data, trains a
  model, evaluates it, and writes a serialized model file (`ml/models/rul_model.pkl`)
  plus a metrics report. It never runs as part of the live demo.
- **`backend/` is the only thing that talks to the trained model at runtime.** It loads
  the `.pkl` file once at startup and serves predictions + fleet logic over REST. This
  means the ML person can retrain and swap the model file without touching backend code,
  and the backend/frontend people are never blocked waiting on model training.
- **`frontend/` never talks to `ml/` directly**, only to `backend/`'s REST API. This
  keeps the contract simple: one API surface (`docs/API_CONTRACTS.md`), one source of
  truth for what the frontend can expect.

This separation is deliberate so that three team members can work in parallel
(see the 3-day plan in `PROJECT_BRAIN.md`) without blocking each other.

---

## 3. Data flow, step by step

1. `ml/src/features.py` reads raw C-MAPSS sensor data, builds sliding-window
   sequences per engine, and engineers degradation-trend features.
2. `ml/src/train.py` trains an XGBoost regressor to predict Remaining Useful Life
   (RUL) in cycles, evaluates it on the official NASA test split, and writes:
   - `ml/models/rul_model.pkl` (the trained model)
   - `ml/models/metrics.json` (MAE, RMSE, and the Healthy/Watch/Urgent confusion matrix)
3. `backend/app/main.py` loads `rul_model.pkl` at startup.
4. `backend/app/routers/fleet.py` combines:
   - live/test-set sensor windows → fed into the model → predicted RUL per engine
   - a synthetic spares table (`backend/app/models/spares.py`) — **illustrative only**
   - a synthetic maintenance-log table — **illustrative only**
   and produces the fleet readiness view defined in `docs/API_CONTRACTS.md`.
5. `frontend/` calls these endpoints and renders:
   - Fleet Overview (all aircraft/engines, status-colour coded)
   - Engine Detail (RUL trend chart, sensor history)
   - Alerts panel (Watch/Urgent engines + linked spares)
   - Baseline-vs-Predictive comparison (the "why this is better" chart)

---

## 4. Health status tiers (used across all layers — keep in sync)

| Tier | Meaning | Colour (frontend) |
|---|---|---|
| **Healthy** | Predicted RUL comfortably above threshold | Green |
| **Watch** | Predicted RUL approaching threshold — monitor, prep spares | Amber |
| **Urgent** | Predicted RUL below safety threshold — schedule maintenance now | Red |

Thresholds are defined once, in `ml/src/config.py`, and must not be duplicated or
redefined elsewhere (backend reads them from the model's metadata, not re-declared).

---

## 5. Why these specific technology choices

- **FastAPI over Flask/Django:** automatic OpenAPI docs (useful for a judge demo —
  you can show `/docs` live), native Pydantic validation, async-ready if needed later.
- **XGBoost over a deep LSTM as the primary model:** faster to train and far easier
  to explain to judges in 60 seconds ("gradient-boosted trees on engineered
  sliding-window features") — an LSTM is a stretch goal only if Day 1 finishes early.
- **React + Vite over Next.js:** we don't need server-side rendering or routing
  complexity for a single-page dashboard; Vite's dev server is fast, which matters
  under a 3-day deadline.
- **Recharts over Chart.js:** React-native component API, less boilerplate for the
  specific charts we need (line charts for RUL trend, bar charts for comparison).
