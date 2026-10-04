"""
Fleet, engine-detail, alerts, spares, and comparison endpoints.
Request/response shapes must match docs/API_CONTRACTS.md exactly — see
docs/BACKEND.md Section 3 for the convention.

NOTE ON CURRENT STATE: this router currently serves DEMO/PLACEHOLDER engine data
(see `_DEMO_ENGINES` below) so the API is runnable and the frontend can be built
against it immediately, in parallel with the ML model being trained (see
docs/ARCHITECTURE.md Section 2 on why the layers are decoupled this way).

TODO (Day 2): replace `_DEMO_ENGINES` with real predictions loaded from
`ml/models/rul_model.pkl` via `app.main`'s loaded model instance, run over the
NASA C-MAPSS test-set engines. Do not remove the illustrative-data honesty rules
when you do this — only the engine/RUL data source changes; spares/maintenance
data stays synthetic and labelled as such.
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AlertItem, AlertsResponse, ComparisonResponse, EngineDetailResponse,
    EngineSummary, FleetResponse, SparesResponse, SparePart, SparePartAlert,
)
from app.models.spares import get_spares_table, link_spares_to_engine

router = APIRouter()

# Healthy/Watch/Urgent thresholds — MUST match ml/src/config.py once the real
# model is wired in. Kept here as placeholders for the demo-data path only.
WATCH_THRESHOLD_CYCLES = 50
URGENT_THRESHOLD_CYCLES = 15


def _status_for_rul(rul: int) -> str:
    if rul <= URGENT_THRESHOLD_CYCLES:
        return "urgent"
    if rul <= WATCH_THRESHOLD_CYCLES:
        return "watch"
    return "healthy"


# Placeholder demo engines — deterministic, not random, so the demo is reproducible.
_DEMO_ENGINES = [
    {"engine_id": f"engine_{i}", "predicted_rul_cycles": rul, "confidence_low": max(rul - 12, 0), "confidence_high": rul + 12}
    for i, rul in enumerate(
        [145, 132, 98, 210, 9, 61, 178, 44, 12, 199, 87, 33, 150, 7, 120, 55, 190, 29, 101, 48],
        start=1,
    )
]


def _summarize(engine: dict) -> EngineSummary:
    status = _status_for_rul(engine["predicted_rul_cycles"])
    return EngineSummary(
        engine_id=engine["engine_id"],
        status=status,
        predicted_rul_cycles=engine["predicted_rul_cycles"],
        confidence_low=engine["confidence_low"],
        confidence_high=engine["confidence_high"],
    )


@router.get("/fleet", response_model=FleetResponse)
def get_fleet() -> FleetResponse:
    summaries = [_summarize(e) for e in _DEMO_ENGINES]
    total = len(summaries)
    healthy = sum(1 for s in summaries if s.status == "healthy")
    watch = sum(1 for s in summaries if s.status == "watch")
    urgent = sum(1 for s in summaries if s.status == "urgent")
    availability = round((healthy / total) * 100, 1) if total else 0.0

    return FleetResponse(
        fleet_availability_pct=availability,
        total_engines=total,
        healthy_count=healthy,
        watch_count=watch,
        urgent_count=urgent,
        engines=summaries,
    )


@router.get("/engine/{engine_id}", response_model=EngineDetailResponse)
def get_engine_detail(engine_id: str) -> EngineDetailResponse:
    engine = next((e for e in _DEMO_ENGINES if e["engine_id"] == engine_id), None)
    if engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")

    status = _status_for_rul(engine["predicted_rul_cycles"])
    linked = [p["part_id"] for p in link_spares_to_engine(engine_id)]

    # TODO (Day 2): replace with real sensor_history pulled from the C-MAPSS test
    # set for this engine, once the ML model + data loader are wired in.
    fake_history = [
        {"cycle": c, "sensor_2": 640 + c * 0.1, "sensor_3": 1580 + c * 0.3}
        for c in range(1, 21)
    ]

    return EngineDetailResponse(
        engine_id=engine_id,
        status=status,
        predicted_rul_cycles=engine["predicted_rul_cycles"],
        confidence_low=engine["confidence_low"],
        confidence_high=engine["confidence_high"],
        sensor_history=fake_history,
        linked_spares=linked,
    )


@router.get("/alerts", response_model=AlertsResponse)
def get_alerts() -> AlertsResponse:
    at_risk = [e for e in _DEMO_ENGINES if _status_for_rul(e["predicted_rul_cycles"]) in ("watch", "urgent")]
    at_risk.sort(key=lambda e: e["predicted_rul_cycles"])

    alerts = [
        AlertItem(
            engine_id=e["engine_id"],
            status=_status_for_rul(e["predicted_rul_cycles"]),
            predicted_rul_cycles=e["predicted_rul_cycles"],
            linked_spares=[SparePartAlert(**p) for p in link_spares_to_engine(e["engine_id"])],
        )
        for e in at_risk
    ]
    return AlertsResponse(alerts=alerts)


@router.get("/spares", response_model=SparesResponse)
def get_spares() -> SparesResponse:
    return SparesResponse(illustrative=True, parts=[SparePart(**p) for p in get_spares_table()])


@router.get("/comparison", response_model=ComparisonResponse)
def get_comparison() -> ComparisonResponse:
    # TODO (Day 2): compute these numbers for real from ml/src/evaluate.py's
    # baseline-vs-predictive simulation on the NASA test set. Placeholder values
    # below are illustrative of the shape only — do not present them as real
    # results in the PPT until replaced.
    return ComparisonResponse(
        fixed_interval_missed_failures=6,
        predictive_missed_failures=1,
        fixed_interval_unnecessary_services=11,
        predictive_unnecessary_services=4,
        total_test_engines=len(_DEMO_ENGINES),
    )
