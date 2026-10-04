# ml/data/

This folder holds the NASA C-MAPSS dataset locally. It is gitignored (data files are
not committed) — only this README is tracked.

**See `docs/DATA.md` for full download instructions.**

Quick version: download the NASA Turbofan Engine Degradation Simulation Data Set,
extract it here so you end up with:

```
ml/data/CMAPSS/
├── train_FD001.txt
├── test_FD001.txt
├── RUL_FD001.txt
```

Start with FD001 only — it's the simplest subset and sufficient to prove the concept
within the 3-day timeline (see `docs/ML.md` Section 1).
