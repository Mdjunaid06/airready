# TESTING.md — AirReady

Given the 3-day deadline, this is intentionally lightweight — enough to catch real
breakage, not a full enterprise test suite. Don't over-invest here at the cost of the
actual product.

---

## 1. ML layer

- `ml/src/evaluate.py` is itself the main "test" — it must be re-runnable against a
  saved model and reproduce the metrics in `ml/models/metrics.json` exactly (same
  seed, same split).
- Before trusting any metric in the PPT, re-run `evaluate.py` fresh and confirm the
  numbers match what's written down — a stale metrics file is an easy, embarrassing
  mistake under deadline pressure.
- Sanity check: predicted RUL should never be negative, and should generally trend
  downward as `cycle` increases for a given engine — spot-check one engine's
  predictions across its full trajectory and eyeball the trend.

---

## 2. Backend layer

Use `pytest`. Minimum coverage for a 3-day prototype — not exhaustive, but real:

```
backend/tests/
├── test_health.py       # GET /health returns 200
├── test_fleet.py          # GET /fleet returns correct shape + counts sum correctly
└── test_engine_detail.py   # GET /engine/{id} — known id returns 200, unknown returns 404
```

Run with:
```bash
cd backend
pytest
```

**Minimum bar:** every endpoint in `docs/API_CONTRACTS.md` has at least one test that
confirms it returns `200` with the documented shape, and that `healthy_count + watch_count
+ urgent_count == total_engines` on `/fleet` (a cheap but real correctness check).

---

## 3. Frontend layer

Manual smoke test is acceptable given the timeline — formal test framework (Vitest/RTL)
is a nice-to-have, not required. Checklist before every demo rehearsal:

- [ ] Fleet Overview loads and shows a non-zero fleet availability percentage
- [ ] Clicking an engine card navigates to Engine Detail and shows its RUL trend chart
- [ ] Alerts panel shows only Watch/Urgent engines, sorted most-urgent first
- [ ] Spares section visibly shows the "illustrative data" label
- [ ] Comparison page renders the baseline-vs-predictive chart with real numbers
- [ ] Reloading any page doesn't break (no blank white screen)
- [ ] Page works at the projector's likely resolution — test at 1280×720, not just your laptop's native resolution

---

## 4. Manual end-to-end QA checklist (run this the night before, not the morning of)

1. Fresh clone of the repo on a clean machine (or at least a fresh terminal) —
   confirm the setup instructions in the root `README.md` actually work as written,
   start to finish, with no undocumented manual steps.
2. Full flow: load Fleet Overview → click into an Urgent engine → see its RUL trend
   → see its linked spare part → go to Comparison → see the baseline-vs-predictive
   numbers.
3. Record a 2–3 minute screen capture of this full flow working, as the ultimate
   fallback if live demo fails on stage (venue wifi, projector issues, etc.).
4. Confirm the numbers shown in the live dashboard match the numbers written in the
   PPT exactly — a mismatch here is an easy, avoidable credibility hit with judges.
