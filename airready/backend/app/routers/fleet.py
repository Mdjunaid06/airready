"""
Fleet, engine-detail, alerts, spares, and comparison endpoints.
Request/response shapes must match docs/API_CONTRACTS.md exactly — see
docs/BACKEND.md Section 3 for the convention.
"""
from math import ceil

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AlertItem, AlertsResponse, ComparisonResponse, EngineDetailResponse,
    EngineSummary, FleetResponse, SparesResponse, SparePart, SparePartAlert,
)
from app.models.spares import get_spares_table, link_spares_to_engine

router = APIRouter()

def _status_for_rul(rul: int, bundle: dict) -> str:
    if rul <= bundle["urgent_threshold_cycles"]:
        return "urgent"
    if rul <= bundle["watch_threshold_cycles"]:
        return "watch"
    return "healthy"


def build_engine_predictions(bundle: dict) -> list[dict]:
    """Run the loaded model on persisted features for the NASA test engines."""
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    error_band = ceil(bundle["mae_cycles"])
    engines = []
    for engine_input in bundle["test_engine_inputs"]:
        features = pd.DataFrame([engine_input["features"]], columns=feature_cols)
        prediction = max(float(model.predict(features)[0]), 0.0)
        predicted_rul = int(round(prediction))
        engines.append({
            "engine_id": engine_input["engine_id"],
            "predicted_rul_cycles": predicted_rul,
            "confidence_low": max(predicted_rul - error_band, 0),
            "confidence_high": predicted_rul + error_band,
            "sensor_history": engine_input["sensor_history"],
            "status": _status_for_rul(predicted_rul, bundle),
        })
    return engines


def _get_runtime_data() -> tuple[dict, list[dict]]:
    from app.main import model_registry

    bundle = model_registry["bundle"]
    engines = model_registry["engines"]
    if bundle is None or engines is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    return bundle, engines


def _summarize(engine: dict) -> EngineSummary:
    return EngineSummary(
        engine_id=engine["engine_id"],
        status=engine["status"],
        predicted_rul_cycles=engine["predicted_rul_cycles"],
        confidence_low=engine["confidence_low"],
        confidence_high=engine["confidence_high"],
    )


@router.get("/fleet", response_model=FleetResponse)
def get_fleet() -> FleetResponse:
    _, engines = _get_runtime_data()
    summaries = [_summarize(e) for e in engines]
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
    _, engines = _get_runtime_data()
    engine = next((e for e in engines if e["engine_id"] == engine_id), None)
    if engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")

    linked = [p["part_id"] for p in link_spares_to_engine(engine_id)]

    return EngineDetailResponse(
        engine_id=engine_id,
        status=engine["status"],
        predicted_rul_cycles=engine["predicted_rul_cycles"],
        confidence_low=engine["confidence_low"],
        confidence_high=engine["confidence_high"],
        sensor_history=engine["sensor_history"],
        linked_spares=linked,
    )


@router.get("/alerts", response_model=AlertsResponse)
def get_alerts() -> AlertsResponse:
    _, engines = _get_runtime_data()
    at_risk = [e for e in engines if e["status"] in ("watch", "urgent")]
    at_risk.sort(key=lambda e: e["predicted_rul_cycles"])

    alerts = [
        AlertItem(
            engine_id=e["engine_id"],
            status=e["status"],
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
    bundle, _ = _get_runtime_data()
    return ComparisonResponse(**bundle["comparison"])
