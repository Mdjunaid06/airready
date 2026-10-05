# ml/data/

The public NASA C-MAPSS FD001 files are committed in `CMAPSS/` for repeatable
teammate setup. Expected files:

**See `docs/DATA.md` for full download instructions.**

If the files are missing, download the NASA Turbofan Engine Degradation Simulation
Data Set and extract FD001 here so you end up with:

```
ml/data/CMAPSS/
├── train_FD001.txt
├── test_FD001.txt
├── RUL_FD001.txt
```

Start with FD001 only — it's the simplest subset and sufficient to prove the concept
within the 3-day timeline (see `docs/ML.md` Section 1). See `docs/DATA.md` for source
details and the full download fallback.
