"""
Feature engineering: drops near-constant sensors, builds sliding-window features
per engine. See docs/ML.md Section 3 for the full pipeline explanation.
"""
import numpy as np
import pandas as pd

from .config import SENSOR_COLUMNS, WINDOW_SIZE


def drop_low_variance_sensors(df: pd.DataFrame, threshold: float = 1e-6) -> list[str]:
    """Returns the list of sensor columns worth keeping (documented, standard
    C-MAPSS preprocessing step — some sensors are near-constant and add only noise).
    Record the dropped list in metrics.json for transparency (docs/ML.md Section 3)."""
    kept = []
    for col in SENSOR_COLUMNS:
        if col in df.columns and df[col].var() > threshold:
            kept.append(col)
    return kept


def normalize_features(df: pd.DataFrame, feature_cols: list[str], stats: dict | None = None):
    """Z-score normalize. If `stats` is given (mean/std from training data), apply
    those instead of recomputing — this is how test data must be normalized, using
    train-set statistics only, to avoid leakage."""
    df = df.copy()
    if stats is None:
        stats = {
            col: {"mean": df[col].mean(), "std": df[col].std() or 1.0}
            for col in feature_cols
        }
    for col in feature_cols:
        df[col] = (df[col] - stats[col]["mean"]) / stats[col]["std"]
    return df, stats


def build_window_features(df: pd.DataFrame, feature_cols: list[str], window: int = WINDOW_SIZE) -> pd.DataFrame:
    """
    For each engine, for each cycle with at least `window` prior cycles available,
    build a flat feature row summarizing the trailing window: mean and std of each
    sensor over the window, plus the most recent reading and the trend (last - first).

    This keeps the feature space compact and fast to train on (vs feeding raw
    sequences into a tree model, which doesn't handle sequences natively) — see
    docs/ML.md Section 4 for why XGBoost is the primary model.
    """
    rows = []
    for engine_id, group in df.groupby("engine_id"):
        group = group.sort_values("cycle").reset_index(drop=True)
        for i in range(window - 1, len(group)):
            window_slice = group.iloc[i - window + 1 : i + 1]
            row = {"engine_id": engine_id, "cycle": group.iloc[i]["cycle"]}
            for col in feature_cols:
                values = window_slice[col].values
                row[f"{col}_mean"] = values.mean()
                row[f"{col}_std"] = values.std()
                row[f"{col}_last"] = values[-1]
                row[f"{col}_trend"] = values[-1] - values[0]
            if "rul" in group.columns:
                row["rul"] = group.iloc[i]["rul"]
            rows.append(row)
    return pd.DataFrame(rows)


def get_feature_column_names(df: pd.DataFrame) -> list[str]:
    """Returns the model-input feature columns (everything except identifiers/target)."""
    exclude = {"engine_id", "cycle", "rul"}
    return [c for c in df.columns if c not in exclude]
