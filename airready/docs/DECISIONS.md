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
