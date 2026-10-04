# AirReady

**SIH 2026 — PS 26249: Air Power — Predictive Maintenance & Fleet Availability**

Predicts aircraft engine Remaining Useful Life (RUL) from sensor data and turns it
into a live fleet-readiness dashboard — instead of fixed-interval or reactive
maintenance. See `docs/PROJECT_BRAIN.md` for the full context.

## Start here

**Read `docs/PROJECT_BRAIN.md` before touching anything.** It is the master context
file: problem statement, non-negotiable rules, repo map, and current status.

| I want to... | Read |
|---|---|
| Understand the whole project | `docs/PROJECT_BRAIN.md` |
| Understand the system design | `docs/ARCHITECTURE.md` |
| Work on the ML model | `docs/ML.md`, `docs/DATA.md` |
| Work on the API | `docs/BACKEND.md`, `docs/API_CONTRACTS.md` |
| Work on the dashboard | `docs/FRONTEND.md` |
| Deploy it | `docs/DEPLOYMENT.md` |
| Test it | `docs/TESTING.md` |
| Understand why a decision was made | `docs/DECISIONS.md` |

## Quick start (see docs for full detail)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:5173`.

## Research & references

See `docs/DECISIONS.md` and `docs/PROJECT_BRAIN.md` for full context. Key sources:

- NASA C-MAPSS Turbofan Engine Degradation Simulation Dataset — NASA Prognostics
  Center of Excellence (PCoE), Ames Research Center.
- USAF Condition-Based Maintenance Plus (CBM+) / PANDA system, built with C3.ai —
  official system of record since 2023, deployed across 1,200+ aircraft.
- IAF × IIT Bombay AI digital-twin programme for the Su-30 MKI fleet — contracts
  signed May 2026.
- India's AMCA 5th-generation fighter Integrated Vehicle Health Management (IVHM)
  programme.
