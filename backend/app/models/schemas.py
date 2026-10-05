"""
Pydantic schemas. These must match docs/API_CONTRACTS.md exactly — if you change a
shape here, update that doc in the same commit (see docs/BACKEND.md Section 3).
"""
from typing import Literal
from pydantic import BaseModel

Status = Literal["healthy", "watch", "urgent"]


class EngineSummary(BaseModel):
    engine_id: str
    status: Status
    predicted_rul_cycles: int
    confidence_low: int
    confidence_high: int


class FleetResponse(BaseModel):
    fleet_availability_pct: float
    total_engines: int
    healthy_count: int
    watch_count: int
    urgent_count: int
    engines: list[EngineSummary]


class SensorReading(BaseModel):
    cycle: int

    class Config:
        extra = "allow"  # sensor_2, sensor_3, etc. are dynamic per dataset subset


class EngineDetailResponse(BaseModel):
    engine_id: str
    status: Status
    predicted_rul_cycles: int
    confidence_low: int
    confidence_high: int
    sensor_history: list[dict]
    linked_spares: list[str]


class SparePartAlert(BaseModel):
    part_id: str
    stock_quantity: int
    lead_time_days: int


class AlertItem(BaseModel):
    engine_id: str
    status: Status
    predicted_rul_cycles: int
    linked_spares: list[SparePartAlert]


class AlertsResponse(BaseModel):
    alerts: list[AlertItem]


class SparePart(BaseModel):
    part_id: str
    part_name: str
    stock_quantity: int
    lead_time_days: int


class SparesResponse(BaseModel):
    illustrative: bool = True
    parts: list[SparePart]


class ComparisonResponse(BaseModel):
    fixed_interval_missed_failures: int
    predictive_missed_failures: int
    fixed_interval_unnecessary_services: int
    predictive_unnecessary_services: int
    total_test_engines: int
