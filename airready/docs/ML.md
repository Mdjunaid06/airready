# ML.md — AirReady

Read `PROJECT_BRAIN.md` and `ARCHITECTURE.md` first. See `DATA.md` for dataset
specifics — this file covers the pipeline: features, model, training, evaluation.

---

## 1. Goal

Given a short recent history of multivariate sensor readings from a turbofan engine,
predict its **Remaining Useful Life (RUL)** — the number of operating cycles left
before it would need major maintenance/failure intervention.

This is a regression problem on NASA's C-MAPSS dataset (see `docs/DATA.md`).

---

## 2. Folder structure

```
ml/
├── requirements.txt
├── data/                     # committed public FD001 benchmark data
│   └── README.md               # dataset location and download fallback (see DATA.md)
├── models/                    # committed demo model artifact and evaluation metrics
│   ├── rul_model.pkl            # the trained model — backend loads this directly
│   └── metrics.json              # MAE, RMSE, confusion matrix — used in the PPT
├── notebooks/                 # exploratory analysis — not production code, keep separate
└── src/
    ├── __init__.py
    ├── config.py                # thresholds, window size, feature list — single source of truth
    ├── data_loader.py             # reads raw C-MAPSS txt files into pandas DataFrames
    ├── features.py                  # sliding-window feature engineering
    ├── train.py                      # trains the model, evaluates, writes model + metrics
    └── evaluate.py                    # standalone evaluation / confusion-matrix report
```

---

## 3. Pipeline, step by step

1. **`data_loader.py`** reads the raw C-MAPSS space-separated text files (train/test/RUL
   files for the chosen subset, e.g. FD001) into pandas DataFrames with named columns:
   `engine_id, cycle, op_setting_1..3, sensor_1..21`.
2. **`features.py`**:
   - Computes the training-set RUL label per row (`max_cycle_for_engine - current_cycle`).
   - Builds sliding windows of `WINDOW_SIZE` cycles (default 30, configurable in
     `config.py`) per engine, so the model sees a short recent trajectory, not a single
     snapshot.
   - Drops sensors with ~zero variance across the dataset (a documented, standard
     preprocessing step for C-MAPSS — list the dropped sensor IDs in `metrics.json`
     for transparency).
   - Normalises remaining features (z-score, fit on train, applied to test).
3. **`train.py`**:
   - Trains an XGBoost regressor (`XGBRegressor`) on the windowed, normalised features.
   - Evaluates on the **official NASA test split** (not a random train/test split —
     using the official split is what makes our MAE/RMSE numbers comparable to published
     benchmarks, which matters for credibility with judges).
   - Converts predicted RUL into the three health tiers (Healthy/Watch/Urgent) using
     thresholds defined in `config.py`, and computes a confusion matrix plus per-tier
     precision, recall, and F1 against the true-RUL-derived tiers.
   - Writes `models/rul_model.pkl` (joblib-serialized) and `models/metrics.json`.
   - The serialized bundle also carries pre-engineered inputs and raw sensor history
     for the official test engines, plus the baseline comparison result. The backend
     uses these demo inputs with the loaded estimator at startup; it does not import ML
     training code or read the raw dataset at request time.
4. **`evaluate.py`** can be re-run standalone against a saved model to regenerate the
   metrics report without retraining — useful right before the demo to double-check
   numbers match what's in the PPT.

---

## 4. Model choice and reasoning

- **Primary model: XGBoost regressor** on engineered window-features (not raw
  sequences). Chosen because: (a) fast to train and iterate on under a 3-day deadline,
  (b) feature importances are easy to show/explain to judges, (c) strong, well-documented
  baseline performance on C-MAPSS in published research.
- **Stretch goal: LSTM/GRU sequence model** (PyTorch) directly on the raw sensor
  sequences, if Day 1 finishes with time to spare. Only attempt this if the XGBoost
  baseline is already working and committed — never let a stretch goal put the working
  baseline at risk.
- **Do not reach for a larger/fancier model "to impress judges."** A well-validated,
  clearly-explained XGBoost model with honest metrics beats an unexplainable deep model
  with suspiciously perfect numbers, every time, in a judged setting.

---

## 5. Evaluation — what to report (and why)

| Metric | Why we report it |
|---|---|
| MAE (cycles) | Standard, comparable metric for C-MAPSS RUL prediction — directly citable against published research |
| RMSE (cycles) | Penalises large misses more — relevant because a large miss is the dangerous failure mode |
| Confusion matrix (Healthy/Watch/Urgent) | Shows false-negative rate directly — the single most important number for a safety-critical system (see `PROJECT_BRAIN.md` rule 2) |
| Per-tier precision and recall | Makes urgent under-triage and the cost of additional inspections visible at the selected operating point |
| Early-catch comparison vs fixed-interval baseline | Compares interval misses and predictive tier misses/false alerts on the official test engines; definitions are kept explicit in `API_CONTRACTS.md` |

**Never report only accuracy or only MAE.** Section 2 of `PROJECT_BRAIN.md` requires the
false-negative framing to be front and centre, not buried.

---

## 6. Reproducibility

- Fix all random seeds (`numpy`, `xgboost`) in `config.py` — a judge re-running your
  code, or a teammate retraining, should get the same numbers.
- `metrics.json` should record: the dataset subset used (e.g. FD001), window size,
  dropped sensors, random seed, final metrics, per-tier precision/recall, and the
  fixed-interval comparison — this file is effectively the
  "lab notebook" for the model and should be treated as a real artifact, not a
  throwaway file.
