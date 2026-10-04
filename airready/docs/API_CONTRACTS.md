# API_CONTRACTS.md — AirReady

This is the exact, current contract between `backend/` and `frontend/`. If you change
an endpoint's shape, update this file in the same commit — this file must always match
`backend/app/models/schemas.py` exactly. Treat any mismatch as a bug.

Base URL (local dev): `http://localhost:8000`

---

## `GET /health`

Simple liveness check.

**Response `200`:**
```json
{ "status": "ok" }
```

---

## `GET /fleet`

Returns the full fleet overview — every engine's current predicted status.

**Response `200`:**
```json
{
  "fleet_availability_pct": 78.5,
  "total_engines": 20,
  "healthy_count": 14,
  "watch_count": 4,
  "urgent_count": 2,
  "engines": [
    {
      "engine_id": "engine_12",
      "status": "healthy",
      "predicted_rul_cycles": 145,
      "confidence_low": 128,
      "confidence_high": 162
    }
  ]
}
```
`status` is one of: `"healthy" | "watch" | "urgent"` (see `ARCHITECTURE.md` Section 4).

---

## `GET /engine/{engine_id}`

Returns detail for a single engine, including recent sensor trend.

**Response `200`:**
```json
{
  "engine_id": "engine_12",
  "status": "healthy",
  "predicted_rul_cycles": 145,
  "confidence_low": 128,
  "confidence_high": 162,
  "sensor_history": [
    { "cycle": 1, "sensor_2": 642.1, "sensor_3": 1589.7 }
  ],
  "linked_spares": ["ENG-BEARING-04"]
}
```

**Response `404`** if `engine_id` is unknown:
```json
{ "detail": "Engine not found" }
```

---

## `GET /alerts`

Returns all engines currently in `watch` or `urgent` status, sorted most-urgent first,
with linked spare-part status — this powers the Alerts panel.

**Response `200`:**
```json
{
  "alerts": [
    {
      "engine_id": "engine_47",
      "status": "urgent",
      "predicted_rul_cycles": 9,
      "linked_spares": [
        { "part_id": "ENG-BEARING-04", "stock_quantity": 3, "lead_time_days": 7 }
      ]
    }
  ]
}
```

---

## `GET /spares`

Returns the full synthetic spares table (illustrative data — see `DATA.md`).

**Response `200`:**
```json
{
  "illustrative": true,
  "parts": [
    {
      "part_id": "ENG-BEARING-04",
      "part_name": "High-pressure compressor bearing",
      "stock_quantity": 3,
      "lead_time_days": 7
    }
  ]
}
```
Note the `"illustrative": true` flag — the frontend uses this to render the
"illustrative data" label required by `PROJECT_BRAIN.md` rule 5.

---

## `GET /comparison`

Returns the baseline (fixed-interval) vs predictive maintenance comparison, computed
on the NASA test set — this is the data behind the "why we're better" chart.

**Response `200`:**
```json
{
  "fixed_interval_missed_failures": 6,
  "predictive_missed_failures": 1,
  "fixed_interval_unnecessary_services": 11,
  "predictive_unnecessary_services": 4,
  "total_test_engines": 20
}
```

---

## Error shape (applies to all endpoints)

Any `4xx`/`5xx` response follows FastAPI's default shape:
```json
{ "detail": "human-readable message" }
```
