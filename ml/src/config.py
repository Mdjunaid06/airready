"""
Single source of truth for ML pipeline configuration: dataset choice, window size,
health-tier thresholds, and random seed.

IMPORTANT: WATCH_THRESHOLD_CYCLES and URGENT_THRESHOLD_CYCLES here must match the
values backend/app/routers/fleet.py uses once Day 2 wires the real model in — see
docs/ARCHITECTURE.md Section 4. Ideally these get exported into metrics.json and
read by the backend from there, rather than hardcoded twice — flag this as a TODO
if you're continuing the project and it hasn't been done yet.
"""

# Which C-MAPSS subset to use. Start with FD001 (see docs/DATA.md).
DATASET_SUBSET = "FD001"
DATA_DIR = "ml/data/CMAPSS"

# Sliding window size (number of recent cycles the model sees per prediction)
WINDOW_SIZE = 30

# Reproducibility
RANDOM_SEED = 42

# Health tier thresholds, in predicted RUL cycles.
# These are a starting point — tune them using the confusion matrix in
# ml/src/evaluate.py, biased toward minimising false negatives (see
# docs/PROJECT_BRAIN.md rule 2 and docs/ML.md Section 5).
WATCH_THRESHOLD_CYCLES = 50
URGENT_THRESHOLD_CYCLES = 15

# Column names for the raw C-MAPSS files (21 sensors + 3 operational settings)
BASE_COLUMNS = ["engine_id", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"]
SENSOR_COLUMNS = [f"sensor_{i}" for i in range(1, 22)]
ALL_COLUMNS = BASE_COLUMNS + SENSOR_COLUMNS

MODEL_OUTPUT_PATH = "ml/models/rul_model.pkl"
METRICS_OUTPUT_PATH = "ml/models/metrics.json"
