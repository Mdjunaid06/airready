"""
ILLUSTRATIVE / SYNTHETIC DATA ONLY.

This module stands in for a real spares/inventory-management system integration,
which the problem statement calls for but which we have no real access to (see
docs/PROJECT_BRAIN.md rule 5 and docs/DATA.md Section 2).

Every response built from this module must carry the `illustrative: true` flag
(see docs/API_CONTRACTS.md) so the frontend can visibly label it as such.

Do not let this data be presented anywhere as if it were real IAF spares records.
"""

# A small, fixed, illustrative spares table. Deliberately simple and readable —
# this is a demonstration of the integration pattern, not a real inventory system.
SYNTHETIC_SPARES = [
    {
        "part_id": "ENG-BEARING-04",
        "part_name": "High-pressure compressor bearing",
        "stock_quantity": 3,
        "lead_time_days": 7,
    },
    {
        "part_id": "ENG-SEAL-11",
        "part_name": "Turbine seal assembly",
        "stock_quantity": 1,
        "lead_time_days": 14,
    },
    {
        "part_id": "ENG-FAN-02",
        "part_name": "Fan blade set",
        "stock_quantity": 5,
        "lead_time_days": 5,
    },
    {
        "part_id": "ENG-SENSOR-07",
        "part_name": "Vibration sensor module",
        "stock_quantity": 8,
        "lead_time_days": 2,
    },
]


def get_spares_table() -> list[dict]:
    """Returns the illustrative spares table. See module docstring."""
    return SYNTHETIC_SPARES


def link_spares_to_engine(engine_id: str) -> list[dict]:
    """
    Deterministically (not randomly) links 1-2 illustrative spare parts to an
    engine ID, purely to demonstrate the data-fusion pattern the PS asks for.
    Deterministic so demo results are reproducible, not different every run.
    """
    index = sum(ord(c) for c in engine_id) % len(SYNTHETIC_SPARES)
    return [SYNTHETIC_SPARES[index]]
