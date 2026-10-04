# BACKEND.md — AirReady

Read `PROJECT_BRAIN.md` and `ARCHITECTURE.md` first. This file is everything you need
to work inside `backend/` without guessing conventions.

---

## 1. Stack

- Python 3.11+
- FastAPI (web framework)
- Uvicorn (ASGI server, used for local dev + production)
- Pydantic v2 (request/response validation and settings)
- joblib (loading the trained model artifact from `ml/`)
- python-dotenv (loading `.env` locally)

---

## 2. Folder structure

```
backend/
├── requirements.txt
├── .env.example          # copy to .env and fill in locally — never commit .env
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app instance, CORS, router registration, startup model load
│   ├── config.py           # Pydantic Settings — reads from .env
│   ├── models/              # Pydantic schemas AND synthetic data generators
│   │   ├── __init__.py
│   │   ├── schemas.py         # request/response models — must match API_CONTRACTS.md exactly
│   │   └── spares.py           # synthetic spares/maintenance-log data (illustrative — see rule in PROJECT_BRAIN.md)
│   └── routers/
│       ├── __init__.py
│       └── fleet.py            # /fleet, /engine/{id}, /alerts, /spares endpoints
```

---

## 3. Conventions (follow these exactly — don't improvise new patterns)

- **Every endpoint's request/response shape is defined in `docs/API_CONTRACTS.md` first,
  as a Pydantic schema in `app/models/schemas.py` second, then implemented in a router.**
  If you need to change a shape, update `API_CONTRACTS.md` in the same commit.
- **Routers are grouped by resource, not by HTTP verb.** One file per resource
  (`fleet.py` covers all fleet/engine/alert endpoints for now; split further only if
  it grows past ~200 lines).
- **Never put business logic directly in a route handler.** Route handlers should be
  thin: parse request → call a function → return response. Put the actual fleet
  readiness / scoring logic in a plain function so it's independently testable
  (see `docs/TESTING.md`).
- **Type-hint everything.** FastAPI's validation and auto-docs depend on it.
- **Config via environment variables only** — never hardcode a port, CORS origin, or
  file path in code. Add new settings to `app/config.py` and `.env.example` together.
- **The model is loaded once, at app startup**, and kept in memory (see `main.py`
  `@app.on_event("startup")` or FastAPI's lifespan pattern) — never reload it per-request.

---

## 4. How to run locally

```bash
cd backend
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env if needed
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the live, auto-generated API docs (FastAPI's
Swagger UI) — this is genuinely useful to show judges live, not just for development.

---

## 5. Environment variables (`.env`)

See `backend/.env.example` for the full, current list with comments. At minimum:

| Variable | Purpose | Example |
|---|---|---|
| `PORT` | Port Uvicorn binds to | `8000` |
| `MODEL_PATH` | Path to the trained model artifact | `../ml/models/rul_model.pkl` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173` |

---

## 6. Error handling convention

- Use FastAPI's `HTTPException` for expected errors (e.g., unknown engine ID → 404).
- Never let a raw exception/stack trace reach the client in a demo — wrap risky logic
  (model inference, file loads) in try/except and return a clean `HTTPException(500, ...)`.
- Log the real error server-side (plain `print` is fine for a 3-day prototype — don't
  over-engineer logging infrastructure under this deadline).

---

## 7. Adding a new endpoint — checklist

1. Define the request/response shape in `docs/API_CONTRACTS.md`.
2. Add the matching Pydantic model(s) to `app/models/schemas.py`.
3. Implement the route in the relevant file under `app/routers/`.
4. Register the router in `app/main.py` if it's a new router file.
5. Add a test (see `docs/TESTING.md`).
6. Manually hit it via `/docs` to confirm the shape matches what you documented.
