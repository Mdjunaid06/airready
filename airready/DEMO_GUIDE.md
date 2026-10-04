# AirReady Demo and Team Setup

Last updated: 2026-10-05

This guide explains what the prototype demonstrates, what each page means, and how to run the ML pipeline, backend, and frontend from a clean Windows clone.

## What the demo is

AirReady is a predictive-maintenance decision-support prototype for SIH 2026 Problem Statement 26249. It estimates turbofan Remaining Useful Life (RUL), assigns a health tier, and displays engine and fleet summaries through a REST API and React dashboard.

The sensor data is NASA's public C-MAPSS FD001 simulated turbofan benchmark, not real aircraft telemetry, classified information, or IAF data. The design is intended to accept real sensor feeds in a future system, but no live telemetry integration is implemented here. Spares inventory is synthetic and illustrative. The per-engine health profile is data-driven; it is not a physics-based engine simulation. Recommendations are for a human maintenance engineer to review, never automatic maintenance actions.

## How the system works

1. `ml/data/CMAPSS/` contains the FD001 training set, held-out test set, and official test RUL labels.
2. `ml/src/data_loader.py` reads the whitespace-separated files. `features.py` adds training RUL labels, drops six near-constant sensors, normalizes the retained sensors with training-set statistics, and builds 30-cycle sliding-window features.
3. `train.py` fits the XGBoost regressor on training engines and evaluates against all 100 engines in the official NASA test split. It writes `ml/models/rul_model.pkl` and `ml/models/metrics.json`.
4. `evaluate.py` scores the fixed-interval and predictive policies on the same test engines, then updates the comparison in both the metrics report and serialized model bundle.
5. FastAPI loads that bundle once at startup. It applies the estimator to the stored held-out engine features and serves current RUL predictions, sensor history, alerts, illustrative spares links, and comparison metrics. Backend request handling does not import ML training code.
6. React calls the backend only through `frontend/src/lib/api.js` and renders the responses.

### Health tiers

The configured thresholds are in `ml/src/config.py` and travel with the model bundle. The tier is based on predicted RUL:

- **Healthy:** predicted RUL is greater than 50 cycles. Green status; no priority alert is raised.
- **Watch:** predicted RUL is greater than 15 and at most 50 cycles. Amber status; review the trend and consider inspection/spares preparation.
- **Urgent:** predicted RUL is at most 15 cycles. Red status; prioritize human maintenance review.

A tier is a model recommendation, not a diagnosis or an order to service an engine. Thresholds are provisional and require calibration with real maintenance-domain data before operational use.

## What each page shows

### Fleet Overview

- The large availability percentage is `healthy_count / total_engines`; it is the visual summary of the current benchmark fleet, not aircraft availability in service.
- Healthy, Watch, and Urgent counts show the predicted tier distribution. Priority review lists Watch/Urgent engines, most urgent first.
- Each engine card links to its detail page and shows predicted RUL and the empirical MAE display band.
- Any linked spare counts or part IDs are illustrative synthetic inventory, clearly labeled as such.

### Engine Detail

- Shows one NASA test engine's predicted RUL, status, an empirical error band based on held-out MAE, and its observed sensor 2/3 history from the truncated test trajectory.
- The MAE band is not a calibrated probability interval.
- Linked part IDs come from the synthetic spares generator. They do not represent a real inventory system.

### Comparison

Compares policy counts on the same 100-engine NASA FD001 held-out split. Current values are 39 fixed-interval misses, 2 predictive urgent downgrades, 33 fixed-interval unnecessary services, and 2 predictive false alerts. They are benchmark simulation results, not measured operational outcomes.

The comparison definitions are deliberately explicit:

- A fixed-interval miss is a test engine with true RUL at or below the 60-cycle service interval.
- A predictive miss is an actually Urgent engine whose predicted tier is not Urgent, including an Urgent-to-Watch downgrade.
- A predictive unnecessary service is a Watch/Urgent prediction when the true tier is Healthy (true RUL above 50 cycles).
- A fixed-interval unnecessary service uses the conservative "comfortably healthy" cutoff of true RUL above 100 cycles (twice the Watch threshold).

The fixed and predictive metrics use the same test engines, but the unnecessary-service definitions differ by policy as stated above. Avoid describing them as live failures or real maintenance actions.

## Current model evaluation

The latest trained FD001 report is in `ml/models/metrics.json`:

- MAE: 19.43 cycles
- RMSE: 26.40 cycles
- Confusion matrix, rows actual and columns predicted in Healthy/Watch/Urgent order: `[[65, 2, 0], [5, 15, 3], [0, 2, 8]]`
- Urgent-tier precision: 0.727; recall: 0.800. Two of ten actual Urgent engines were predicted Watch; none were predicted Healthy.

These are results on NASA's public simulated benchmark only. The fixed-interval comparison is generated separately by `evaluate.py`.

## Repository contents

- `ml/`: dataset, reproducible feature/training/evaluation code, model bundle, and metrics report.
- `backend/`: FastAPI service, schemas, routes, tests, and environment template.
- `frontend/`: React/Vite dashboard, API client, pages, components, and environment template.
- `docs/`: architecture, data, API contract, testing, deployment, project rules, and decisions.

The FD001 text files and the small trained model bundle are committed for teammate onboarding. `.env`, `.env.local`, virtual environments, `node_modules`, and build output are excluded. The trained model can also be regenerated locally from the committed dataset.

## Fresh Windows setup

Prerequisites: Git, Python 3.11 or later, and Node.js 18 or later with npm. Run the commands below in PowerShell. Replace `<repository-url>` with the team's Git remote URL.

### 1. Clone or update

For a fresh machine:

```powershell
git clone <repository-url>
Set-Location .\airready
```

For an existing clone:

```powershell
Set-Location <path-to-clone>
git pull --ff-only origin main
```

Verify the benchmark files are present:

```powershell
Get-ChildItem .\ml\data\CMAPSS
```

Expected files: `train_FD001.txt`, `test_FD001.txt`, and `RUL_FD001.txt`. They are tracked in this repository. If using an older clone or the files are absent, download NASA's Turbofan Engine Degradation Simulation Data Set as described in `docs/DATA.md`, then extract those three FD001 files into `ml/data/CMAPSS/` without renaming them.

### 2. Create local environment files

The templates are committed; the real env files are ignored and must stay local. These commands only copy a template when the destination does not already exist, so they preserve teammate-specific values:

```powershell
if (!(Test-Path .\backend\.env)) { Copy-Item .\backend\.env.example .\backend\.env }
if (!(Test-Path .\frontend\.env.local)) { Copy-Item .\frontend\.env.example .\frontend\.env.local }
```

For the default ports, confirm `backend/.env` contains:

```dotenv
PORT=8000
MODEL_PATH=../ml/models/rul_model.pkl
CORS_ORIGINS=http://localhost:5173
```

Confirm `frontend/.env.local` contains:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

`MODEL_PATH` is relative to the backend working directory. Do not commit either real env file or put secrets in this project; current settings are local URLs and paths only.

### 3. Optional: train or refresh the model

The model bundle is committed, so training is optional for a first run. To reproduce it or refresh after changing ML code, run from the repository root:

```powershell
python -m venv .venv-ml
.\.venv-ml\Scripts\python.exe -m pip install -r .\ml\requirements.txt
.\.venv-ml\Scripts\python.exe -m ml.src.train
.\.venv-ml\Scripts\python.exe -m ml.src.evaluate
```

Training creates/updates `ml/models/rul_model.pkl` and `ml/models/metrics.json`. Evaluation refreshes the comparison in both files without retraining. Run it before starting/restarting the backend so the API loads the latest bundle.

### 4. Start the backend

Open a PowerShell terminal from the repository root, then run:

```powershell
python -m venv .venv-backend
.\.venv-backend\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Set-Location .\backend
..\.venv-backend\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Keep this terminal running. Check `http://localhost:8000/health`, then open `http://localhost:8000/docs` for Swagger UI. The model path resolves because Uvicorn is started from `backend/`.

### 5. Start the frontend

Open a second PowerShell terminal from the repository root:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Open the Vite URL printed in that terminal; by default it is `http://localhost:5173`. Vite reads `frontend/.env.local` when it starts, so restart Vite after changing the API URL.

### 6. Verify the demo

- `GET /health` should return `{"status":"ok"}`.
- In Swagger, check `/fleet`, `/engine/engine_1`, `/alerts`, `/spares`, and `/comparison`.
- The fleet should contain 100 test engines; `/spares` must return `"illustrative": true`.
- Open Fleet Overview, select an engine, review its RUL/sensor trend, then open Comparison.
- Backend tests: from `backend/`, run `..\.venv-backend\Scripts\python.exe -m pytest`.
- ML comparison test: from the repository root, run `.\.venv-ml\Scripts\python.exe -m unittest ml.test_evaluate`.

### If default ports are occupied

Choose ports explicitly and keep the browser origin, CORS setting, and API URL aligned. For example, use backend port 8001 and frontend port 5174:

1. Set `CORS_ORIGINS=http://localhost:5174` in `backend/.env`.
2. Set `VITE_API_BASE_URL=http://localhost:8001` in `frontend/.env.local`.
3. Start the backend from `backend/` with `..\.venv-backend\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001`.
4. Start Vite from `frontend/` with `npm run dev -- --port 5174`.
5. Open `http://localhost:5174` and Swagger at `http://localhost:8001/docs`.

CORS compares the exact browser origin, including host and port. If you browse using `127.0.0.1` instead of `localhost`, use that exact host in `CORS_ORIGINS`.

## Data and safety boundaries

Never claim access to real classified/IAF data. Refer to NASA C-MAPSS as a public benchmark proxy. Keep synthetic spares visibly labeled illustrative. Do not call the dashboard a thermodynamic digital twin; it shows a data-driven per-engine health profile. Keep all risk flags and maintenance suggestions as human-reviewed decision support.
