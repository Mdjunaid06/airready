"""Recomputes the baseline-vs-predictive comparison without retraining.

The comparison is written to metrics.json and the serialized model bundle so
the backend can serve the same evaluated result after its next startup.

Run from repo root: python -m ml.src.evaluate
See docs/TESTING.md Section 1 — re-run this before trusting any number in the PPT.
"""
import json
from pathlib import Path

import joblib
import numpy as np

from .config import (
    METRICS_OUTPUT_PATH,
    MODEL_OUTPUT_PATH,
    URGENT_THRESHOLD_CYCLES,
    WATCH_THRESHOLD_CYCLES,
)
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
    Compare a fixed service interval with predicted health tiers.

    A fixed-interval service is late when true RUL is no greater than the
    interval. A predictive miss is an actually urgent engine not predicted
    urgent, including a downgrade to watch. A predictive unnecessary service
    is a watch/urgent prediction for an engine whose true tier is healthy.
    Fixed unnecessary service retains the conservative "comfortably healthy"
    definition: true RUL greater than twice the watch threshold.
    """
    fixed_missed = sum(1 for rul in y_true if rul <= fixed_interval_cycles)
    fixed_unnecessary = sum(1 for rul in y_true if rul > WATCH_THRESHOLD_CYCLES * 2)

    predictive_missed = sum(
        1 for true_r, pred_r in zip(y_true, y_pred)
        if _status_for_rul(true_r) == "urgent" and _status_for_rul(pred_r) != "urgent"
    )
    predictive_unnecessary = sum(
        1 for true_r, pred_r in zip(y_true, y_pred)
        if _status_for_rul(true_r) == "healthy" and _status_for_rul(pred_r) != "healthy"
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
    y_pred = np.maximum(model.predict(X_test), 0)

    comparison = compute_baseline_vs_predictive(true_rul[: len(y_pred)], y_pred)
    saved["comparison"] = comparison
    joblib.dump(saved, MODEL_OUTPUT_PATH)

    metrics_path = Path(METRICS_OUTPUT_PATH)
    metrics = json.loads(metrics_path.read_text())
    metrics["comparison"] = comparison
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n")

    print(json.dumps(comparison, indent=2))
    return comparison


if __name__ == "__main__":
    main()
