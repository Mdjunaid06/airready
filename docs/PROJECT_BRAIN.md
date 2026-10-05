# PROJECT_BRAIN.md — AirReady

> **Read this file first.** This is the single source of truth for the project's purpose,
> constraints, and non-negotiable rules. Any human or AI assistant picking up this project —
> at any point, in any session — should read this file before writing a single line of code.
> If something in another doc or in the existing code ever contradicts this file, **this file
> wins**, and the contradiction should be flagged, not silently resolved.

---

## 1. What this project is

**Project name:** AirReady
**Built for:** Smart India Hackathon (SIH) 2026, Problem Statement **26249**
**PS Title:** Air Power — Predictive Maintenance & Fleet Availability
**Owning Ministry:** Ministry of Defence (MoD), Defence Services Staff College
**Category:** Software — Transportation & Logistics

**One-line pitch:** AirReady predicts when an aircraft engine will need maintenance —
*before* it fails — and turns that prediction into a live, fleet-wide readiness dashboard,
instead of relying on fixed-interval or reactive (after-failure) maintenance.

**Full problem statement (verbatim, do not paraphrase away the nuance):**
> Low aircraft availability due to fragmented and largely reactive maintenance practices
> across the air fleet. Maintenance data from aircraft health-monitoring systems, technical
> records, spares and maintenance agencies is not adequately integrated, resulting in
> delayed fault prediction, avoidable aircraft downtime and sub-optimal utilisation of
> critical assets.
>
> Technology Opportunity: AI/ML-based predictive maintenance, IoT/aircraft health
> monitoring, digital twins and an integrated maintenance analytics platform.

---

## 2. Non-negotiable rules (read before touching anything)

These rules exist because they were deliberately decided after research and critical
questioning (see `docs/DECISIONS.md` for the reasoning). **Do not silently violate them
to "improve" the demo** — if a rule seems wrong, raise it, don't just override it.

1. **Never claim access to real classified/IAF data.** We use NASA's public C-MAPSS
   turbofan degradation dataset as an honest, stated proxy for real aircraft
   health-monitoring sensor data. Every doc, every slide, every line of UI copy that
   could imply "real military data" must instead say "NASA C-MAPSS (public benchmark
   dataset), architecture designed to plug into real sensor feeds."
2. **Bias the model toward safety, not accuracy headlines.** We deliberately minimise
   false negatives (missed failures) even if it costs more false positives (extra
   inspections). Never tune thresholds purely to maximise an accuracy number — report
   precision/recall and justify the chosen operating point.
3. **"Digital twin" means a data-driven per-engine health profile**, not a
   physics-informed simulation. Do not let UI copy, docs, or the pitch drift into
   implying we modelled real engine thermodynamics — we did not.
4. **The AI is a decision-support layer, not an autonomous decision-maker.** Every
   place the UI shows a recommendation, it must be framed as a recommendation for a
   human maintenance engineer to review, not an automatic action.
5. **Synthetic data (spares, maintenance logs) must be labelled as illustrative**,
   both in code comments and in any UI that displays it. Never let synthetic numbers
   be presented as if they were real IAF figures.
6. **Keep the three layers (ML, Backend, Frontend) loosely coupled.** The backend
   should never import ML training code directly — it loads a trained, serialized
   model artifact (see `docs/ML.md` and `docs/ARCHITECTURE.md`). This keeps the system
   demoable even if the ML pipeline is mid-change.
7. **Any new API endpoint must be added to `docs/API_CONTRACTS.md` in the same change.**
   Docs and code must never drift apart — a future session (human or AI) should be able
   to trust the docs completely instead of re-reading all the code.

---

## 3. Repo map — what lives where

```
airready/
├── docs/                  # <- you are here. All project knowledge lives here.
│   ├── PROJECT_BRAIN.md   # this file — master context, rules, status
│   ├── ARCHITECTURE.md    # system design, data flow, component diagram
│   ├── BACKEND.md         # FastAPI service: structure, conventions, how to run
│   ├── FRONTEND.md        # dashboard app: structure, conventions, how to run
│   ├── ML.md              # model pipeline: data, features, training, evaluation
│   ├── DATA.md            # dataset details, schemas, download instructions
│   ├── API_CONTRACTS.md   # exact request/response shape of every endpoint
│   ├── DEPLOYMENT.md      # how to ship this to a live URL
│   ├── TESTING.md         # how to test each layer + manual QA checklist
│   └── DECISIONS.md       # append-only log of key decisions and why
├── backend/               # FastAPI service — serves predictions + fleet data
├── ml/                    # data pipeline, feature engineering, model training
├── frontend/              # React dashboard — the thing judges actually look at
├── .gitignore
└── README.md              # quick-start pointer, links into docs/
```

---

## 4. Tech stack (summary — see per-layer docs for detail)

| Layer | Stack |
|---|---|
| ML | Python, pandas, scikit-learn, XGBoost (LSTM via PyTorch is a stretch goal) |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Frontend | React + Vite, Tailwind CSS, Recharts, Axios |
| Data | NASA C-MAPSS (public), synthetic spares/maintenance-log tables |
| Deployment | Backend → Render; Frontend → Vercel (see `docs/DEPLOYMENT.md`) |

---

## 5. Current status

> **Update this section at the end of every work session.** This is how the next
> person (or AI) picking this up knows exactly where things stand without reading
> every file.

- [x] Repo scaffolded (this commit)
- [x] NASA C-MAPSS FD001 dataset placed in `ml/data/CMAPSS/`
- [x] Feature engineering pipeline written (`ml/src/features.py`)
- [x] RUL model trained and evaluated (`ml/src/train.py`): MAE 19.43 cycles, RMSE 26.40 cycles; urgent precision 0.727, recall 0.800 at configured thresholds
- [x] Model exported to `ml/models/rul_model.pkl`; metrics and confusion matrix recorded in `ml/models/metrics.json`
- [x] Backend endpoints implemented against `docs/API_CONTRACTS.md` and backed by the trained model
- [x] Frontend dashboard wired to the live backend and smoke-tested at desktop and mobile widths
- [x] Baseline-vs-predictive comparison chart working on the 100-engine NASA FD001 test set
- [ ] End-to-end demo rehearsed

**Last updated by:** GitHub Copilot / 2026-10-04
**Current blocker, if any:** End-to-end demo rehearsal remains. Ports 8000 and 5173 were already occupied during verification, so the updated backend and frontend were tested on 8001 and 5174.

---

## 6. The 3-day build plan this repo follows

| Day | Focus | Primary docs to read |
|---|---|---|
| Day 1 | Data + RUL prediction model | `docs/DATA.md`, `docs/ML.md` |
| Day 2 | Fleet logic, data fusion, baseline comparison | `docs/ML.md`, `docs/BACKEND.md`, `docs/API_CONTRACTS.md` |
| Day 3 | Dashboard, polish, demo rehearsal | `docs/FRONTEND.md`, `docs/TESTING.md`, `docs/DEPLOYMENT.md` |

---

## 7. If you are an AI continuing this project

1. Read this file completely.
2. Read `docs/DECISIONS.md` to understand *why* things are the way they are, not just *what* they are.
3. Read the doc for the layer you're about to touch (`BACKEND.md`, `FRONTEND.md`, or `ML.md`).
4. Check Section 5 (Current status) above before assuming anything is or isn't done.
5. If you make an architectural decision, append it to `docs/DECISIONS.md` — don't just make the change silently.
6. If you add or change an API endpoint, update `docs/API_CONTRACTS.md` in the same change.
7. Never violate Section 2 (Non-negotiable rules) to make a demo look more impressive.
