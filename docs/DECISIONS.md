# DECISIONS.md — AirReady

**Append-only.** Never edit or delete a past entry — if a decision is later reversed,
add a new entry that says so and references the old one. This file is the project's
memory of *why*, which matters more than *what* once a project has multiple
contributors (human or AI) across multiple sessions.

Format per entry: Date, Decision, Reasoning, Alternatives considered.

---

### 2026-10-03 — Chose PS 26249 over PS 26250

**Decision:** Build for PS 26249 (Predictive Maintenance & Fleet Availability) rather
than PS 26250 (Dynamic Air Operations & Resource Optimisation).

**Reasoning:** PS 26249 has a real, public, rigorous benchmark dataset available
(NASA C-MAPSS), which removes most of Day-1 data risk and gives us citable, credible
accuracy numbers. PS 26250's "real-time, multi-source fusion, contested environment"
framing has more moving, harder-to-fake parts for a 3-day build and would rely more
heavily on synthetic data across many categories (airspace, threats, weather, weapons
loads) at once.

**Alternatives considered:** PS 26250 was a close second; submission counts (4 vs 6
out of 500) were close enough not to be decisive on their own.

---

### 2026-10-03 — Use NASA C-MAPSS as a stated public proxy, not real IAF data

**Decision:** Train and evaluate the RUL model on NASA's C-MAPSS dataset, and state
this openly everywhere (docs, UI, pitch) rather than implying real military data.

**Reasoning:** We have no legitimate access to classified/real IAF sensor data.
Claiming otherwise would be dishonest and would not survive judge cross-questioning.
C-MAPSS is a real, peer-reviewed, industry-standard benchmark for exactly this
prediction problem, which makes our metrics genuinely comparable to published
research — a stronger, more defensible position than inventing synthetic sensor
data from scratch.

**Alternatives considered:** Fully synthetic data generation (rejected — less
credible, not independently verifiable, and NASA's dataset already does this job
better than we could).

---

### 2026-10-03 — XGBoost as primary model, LSTM as stretch goal only

**Decision:** Build the core RUL predictor as an XGBoost regressor on engineered
window-features; only attempt an LSTM if time remains after the baseline works.

**Reasoning:** Under a 3-day deadline, a well-validated, explainable model that is
definitely working beats a fancier model that might not be finished or well-tuned in
time. XGBoost also has strong, well-documented baseline performance on C-MAPSS in
published research, which supports benchmarking claims.

**Alternatives considered:** LSTM/GRU sequence model as the primary approach
(rejected as primary — too much training/tuning risk under the timeline; kept as an
optional stretch goal).

---

### 2026-10-03 — Three-layer architecture (ml / backend / frontend), loosely coupled

**Decision:** Split the system into an offline `ml/` training pipeline, a `backend/`
service that only loads a serialized model, and a `frontend/` that only talks to the
backend's REST API — never directly to `ml/`.

**Reasoning:** Allows up to three team members to work in parallel without blocking
each other (see the 3-day plan in `PROJECT_BRAIN.md`), and means the ML model can be
retrained and swapped without touching backend or frontend code.

**Alternatives considered:** A single monolithic Python app serving both the model
and the API together with a server-rendered UI (rejected — would block frontend work
on backend/ML completion, and server-rendered UI is weaker for an interactive,
visually-driven judge demo).

---

<!-- Add new entries below this line, most recent at the bottom -->

### 2026-10-04 — Bundle benchmark inference inputs with the model artifact

**Decision:** Store the official FD001 test-engine feature vectors, their observed sensor histories, tier thresholds, and baseline comparison result alongside the trained estimator. The backend loads this bundle once and runs the estimator over those inputs. Use the held-out MAE as an empirical display band for the existing `confidence_low` / `confidence_high` API fields, and describe it in the UI as an error band rather than a calibrated confidence interval.

**Reasoning:** The demo can serve real NASA benchmark predictions and sensor histories without making the backend import ML training/evaluation code or depend on reading the raw dataset at runtime. Persisting the comparison computed by `compute_baseline_vs_predictive()` keeps the API contract unchanged and makes the source evaluation reproducible. Calling the bounds an empirical MAE band avoids implying statistical calibration that the pipeline does not perform.

**Alternatives considered:** Recompute features and comparison inside the backend (rejected — violates the ML/backend separation); hardcode per-engine results or comparison values (rejected — placeholder data); present the MAE band as a probabilistic confidence interval (rejected — unsupported by current calibration).

### 2026-10-04 — Report safety-tier recall without tuning to accuracy

**Decision:** Keep the configured Watch (50-cycle) and Urgent (15-cycle) cutoffs for this evaluation, and record precision, recall, F1, support, and the confusion matrix for every tier. Treat these thresholds as provisional pending maintenance-domain calibration.

**Reasoning:** On the official FD001 test split, urgent recall is 0.800 (8 of 10 true urgent engines were labeled urgent); the other two were labeled watch, and none were labeled healthy. Showing those misses and the tier precision keeps safety performance visible without tuning on headline accuracy or obscuring extra-inspection tradeoffs.

**Alternatives considered:** Retune cutoffs to maximize overall accuracy on the official test set (rejected — conflicts with the safety-first rule and overfits the evaluation split); claim the current thresholds are operationally calibrated (rejected — no real fleet maintenance data is available).

### 2026-10-05 — Track FD001 data and model for clone reproducibility

**Decision:** Commit the public FD001 C-MAPSS text files and the small trained model artifact so a teammate can clone the repository and run the backend immediately. Continue excluding real `.env` files, local environments, dependencies, and build output.

**Reasoning:** The benchmark files total about 5.5 MiB and the model about 1 MiB, well within normal GitHub file limits. Tracking them removes a fragile manual data/model handoff while preserving the ability to regenerate both from the training pipeline. No secrets or operational aircraft data belong in the repository.

**Alternatives considered:** Track only a dataset pointer and require every teammate to find/download/extract the benchmark (rejected — onboarding failures); use Git LFS (unnecessary for these file sizes); commit local env files (rejected — machine-specific and may later contain secrets).

### 2026-10-05 — Score tier downgrades and correct interval misses

**Decision:** Count an actual urgent engine predicted as watch as a predictive miss, count any at-risk prediction on an actually healthy engine as a predictive unnecessary service, and treat true RUL at or below the fixed service interval as a fixed-interval miss. Persist standalone evaluation results to both `metrics.json` and the model bundle consumed by the backend.

**Reasoning:** Per-engine diagnostics showed two urgent-to-watch downgrades and two healthy-to-watch false alerts hidden by predicates that only counted healthy under-predictions and required true RUL above twice the watch threshold. The fixed-interval predicate also counted engines with more than 60 cycles remaining as misses, reversing the one-interval failure condition. Using the existing tier boundaries exposes these errors without tuning model thresholds.

**Alternatives considered:** Keep watch downgrades out of the miss count (rejected — hides failure to escalate an urgent true tier); keep the `> 2 × watch` criterion for predictive false alerts (rejected — inconsistent with the actual healthy-tier boundary); count RUL above the interval as a miss (rejected — service would be due before failure under the stated interval assumption).
