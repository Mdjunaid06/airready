"""
Reads the raw, space-separated NASA C-MAPSS text files into pandas DataFrames.
See docs/DATA.md for where to download the data and docs/ML.md Section 3 for the
pipeline this feeds into.
"""
import pandas as pd
from pathlib import Path

from .config import ALL_COLUMNS, DATA_DIR, DATASET_SUBSET


def _load_raw_file(path: Path) -> pd.DataFrame:
    """C-MAPSS files are space-separated with no header and trailing whitespace
    that creates extra empty columns if not handled — this strips those."""
    df = pd.read_csv(path, sep=r"\s+", header=None)
    df = df.iloc[:, : len(ALL_COLUMNS)]
    df.columns = ALL_COLUMNS
    return df


def load_train_data(subset: str = DATASET_SUBSET) -> pd.DataFrame:
    path = Path(DATA_DIR) / f"train_{subset}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. See docs/DATA.md for download instructions — "
            f"the dataset is not included in this repo and must be downloaded locally."
        )
    return _load_raw_file(path)


def load_test_data(subset: str = DATASET_SUBSET) -> pd.DataFrame:
    path = Path(DATA_DIR) / f"test_{subset}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. See docs/DATA.md for download instructions."
        )
    return _load_raw_file(path)


def load_test_rul_labels(subset: str = DATASET_SUBSET) -> pd.Series:
    """The official true RUL for each engine in the test set, at the point its
    trajectory was truncated. This is what evaluate.py scores predictions against."""
    path = Path(DATA_DIR) / f"RUL_{subset}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. See docs/DATA.md for download instructions."
        )
    return pd.read_csv(path, header=None).iloc[:, 0]


def add_train_rul_labels(train_df: pd.DataFrame) -> pd.DataFrame:
    """For training data, RUL at each row = (that engine's max cycle) - (current cycle),
    since training trajectories run all the way to failure."""
    max_cycle = train_df.groupby("engine_id")["cycle"].transform("max")
    train_df = train_df.copy()
    train_df["rul"] = max_cycle - train_df["cycle"]
    return train_df
