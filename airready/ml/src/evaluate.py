"""
Re-generates the metrics report from a saved model, without retraining.
Also computes the fixed-interval-vs-predictive comparison used in /comparison
and the PPT's "why we're better" chart.

Run from repo root: python -m ml.src.evaluate
See docs/TESTING.md Section 1 — re-run this before trusting any number in the PPT.
"""
import json

import joblib
import numpy as np

from .config import URGENT_THRESHOLD_CYCLES, WATCH_THRESHOLD_CYCLES, MODEL_OUTPUT_PATH
from .data_loader import load_test_data, load_test_rul_labels
from .features import build_window_features, normalize_features


def _status_for_rul(rul: float) -> str:
    if rul <= URGENT_THRESHOLD_CYCLES:
        return "urgent"
    if rul <= WATCH_THRESHOLD_CYCLES:
        return "watch"
    return "healthy"


def compute_baseline_vs_predictive(y_true, y_pred, fixed_interval_cycles: int = 60) -> dict:
    """
    Simulates a naive fixed-interval maintenance policy (service every N cycles
    regardless of condition) on the same test engines, and compares it against
    our predictive approach.

    "Missed failure" = the policy would NOT have flagged the engine before its
    true RUL ran out. "Unnecessary service" = the policy triggers service while
    the engine was still comfortably healthy (true RUL still well above threshold).
    """
    fixed_missed = sum(1 for rul in y_true if rul > fixed_interval_cycles)
    fixed_unnecessary = sum(1 for rul in y_true if rul > WATCH_THRESHOLD_CYCLES * 2)

    predictive_missed = sum(
        1 for true_r, pred_r in zip(y_true, y_pred)
        if _status_for_rul(pred_r) == "healthy" and true_r <= URGENT_THRESHOLD_CYCLES
    )
    predictive_unnecessary = sum(
        1 for true_r, pred_r in zip(y_true, y_pred)
        if _status_for_rul(pred_r) in ("watch", "urgent") and true_r > WATCH_THRESHOLD_CYCLES * 2
    )

    return {
        "fixed_interval_missed_failures": int(fixed_missed),
        "predictive_missed_failures": int(predictive_missed),
        "fixed_interval_unnecessary_services": int(fixed_unnecessary),
        "predictive_unnecessary_services": int(predictive_unnecessary),
        "total_test_engines": len(y_true),
    }


def main():
    saved = joblib.load(MODEL_OUTPUT_PATH)
    model, feature_cols, norm_stats, kept_sensors = (
        saved["model"], saved["feature_cols"], saved["norm_stats"], saved["kept_sensors"],
    )

    test_df = load_test_data()
    test_df, _ = normalize_features(test_df, kept_sensors, stats=norm_stats)
    true_rul = load_test_rul_labels().values

    test_features = build_window_features(test_df, kept_sensors)
    last_window = test_features.sort_values("cycle").groupby("engine_id").tail(1).sort_values("engine_id")

    X_test = last_window[feature_cols]
    y_pred = model.predict(X_test)

    comparison = compute_baseline_vs_predictive(true_rul[: len(y_pred)], y_pred)
    print(json.dumps(comparison, indent=2))
    return comparison


if __name__ == "__main__":
    main()
