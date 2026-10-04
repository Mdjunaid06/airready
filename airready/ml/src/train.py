"""
Trains the RUL prediction model end-to-end and writes:
  - ml/models/rul_model.pkl    (trained model, consumed by the backend)
  - ml/models/metrics.json      (MAE, RMSE, confusion matrix — used in the PPT)

Run from the repo root with:  python -m ml.src.train
See docs/ML.md for the full pipeline explanation and docs/DATA.md for how to get
the dataset onto your machine first — this script will raise a clear
FileNotFoundError with instructions if the data isn't there yet.
"""
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import confusion_matrix, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from .config import (
    METRICS_OUTPUT_PATH, MODEL_OUTPUT_PATH, RANDOM_SEED,
    URGENT_THRESHOLD_CYCLES, WATCH_THRESHOLD_CYCLES,
)
from .data_loader import add_train_rul_labels, load_test_data, load_test_rul_labels, load_train_data
from .features import build_window_features, drop_low_variance_sensors, get_feature_column_names, normalize_features


def _status_for_rul(rul: float) -> str:
    if rul <= URGENT_THRESHOLD_CYCLES:
        return "urgent"
    if rul <= WATCH_THRESHOLD_CYCLES:
        return "watch"
    return "healthy"


def main():
    print("Loading training data...")
    train_df = load_train_data()
    train_df = add_train_rul_labels(train_df)

    print("Selecting sensors...")
    kept_sensors = drop_low_variance_sensors(train_df)
    dropped_sensors = [s for s in train_df.columns if s.startswith("sensor_") and s not in kept_sensors]
    print(f"Kept {len(kept_sensors)} sensors, dropped {len(dropped_sensors)}: {dropped_sensors}")

    print("Normalizing...")
    train_df, norm_stats = normalize_features(train_df, kept_sensors)

    print("Building window features (train)...")
    train_features = build_window_features(train_df, kept_sensors)
    feature_cols = get_feature_column_names(train_features)

    X_train = train_features[feature_cols]
    y_train = train_features["rul"]

    print(f"Training XGBoost on {len(X_train)} windowed samples...")
    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        random_state=RANDOM_SEED,
    )
    model.fit(X_train, y_train)

    print("Evaluating on official NASA test split...")
    test_df = load_test_data()
    test_df, _ = normalize_features(test_df, kept_sensors, stats=norm_stats)
    true_rul = load_test_rul_labels()

    # For the test set, take only the LAST window per engine (matches how the
    # official evaluation works — the test trajectories are already truncated).
    test_features = build_window_features(test_df, kept_sensors)
    last_window_per_engine = test_features.sort_values("cycle").groupby("engine_id").tail(1)
    last_window_per_engine = last_window_per_engine.sort_values("engine_id")

    X_test = last_window_per_engine[feature_cols]
    y_pred = model.predict(X_test)
    y_true = true_rul.values[: len(y_pred)]

    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred, squared=False)

    true_status = [_status_for_rul(r) for r in y_true]
    pred_status = [_status_for_rul(r) for r in y_pred]
    labels = ["healthy", "watch", "urgent"]
    cm = confusion_matrix(true_status, pred_status, labels=labels).tolist()

    metrics = {
        "dataset_subset": "FD001",
        "window_size": int(X_train.shape[0] and 30),
        "random_seed": RANDOM_SEED,
        "dropped_sensors": dropped_sensors,
        "mae_cycles": round(float(mae), 2),
        "rmse_cycles": round(float(rmse), 2),
        "confusion_matrix_labels": labels,
        "confusion_matrix": cm,
        "watch_threshold_cycles": WATCH_THRESHOLD_CYCLES,
        "urgent_threshold_cycles": URGENT_THRESHOLD_CYCLES,
    }

    Path("ml/models").mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "feature_cols": feature_cols, "norm_stats": norm_stats, "kept_sensors": kept_sensors}, MODEL_OUTPUT_PATH)
    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nDone. MAE={metrics['mae_cycles']} cycles, RMSE={metrics['rmse_cycles']} cycles")
    print(f"Model saved to {MODEL_OUTPUT_PATH}")
    print(f"Metrics saved to {METRICS_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
