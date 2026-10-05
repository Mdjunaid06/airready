# FRONTEND.md — AirReady

Read `PROJECT_BRAIN.md` and `ARCHITECTURE.md` first.

---

## 1. Stack

- React 18 + Vite
- Tailwind CSS (utility-first styling — no separate CSS files per component unless truly needed)
- Recharts (charts — RUL trend lines, baseline-vs-predicted bar charts)
- Axios (API calls)
- React Router (only if we end up with more than the planned 3–4 views)

---

## 2. Folder structure

```
frontend/
├── package.json
├── .env.example            # copy to .env.local — VITE_API_BASE_URL
├── index.html
├── src/
│   ├── main.jsx              # entry point
│   ├── App.jsx                 # top-level layout + routing
│   ├── lib/
│   │   └── api.js                # single Axios instance + API call functions — nothing else calls Axios directly
│   ├── pages/
│   │   ├── FleetOverview.jsx      # the main dashboard — list/grid of all engines, colour-coded
│   │   ├── EngineDetail.jsx        # RUL trend chart + sensor history for one engine
│   │   └── Comparison.jsx           # baseline (fixed-interval) vs predictive — the "why we're better" view
│   └── components/
│       ├── StatusBadge.jsx          # Healthy/Watch/Urgent pill — single source of the colour logic
│       ├── FleetCard.jsx             # one aircraft/engine card on the Fleet Overview grid
│       ├── RulTrendChart.jsx          # Recharts line chart, reused on EngineDetail
│       └── AlertsPanel.jsx             # Watch/Urgent list + linked spares status
```

---

## 3. Conventions

- **All API calls go through `src/lib/api.js`.** No component calls `axios` directly —
  this keeps the API contract in one place and makes it trivial to mock for testing.
- **Status colour logic lives only in `StatusBadge.jsx`.** Every other component that
  needs to show Healthy/Watch/Urgent imports and reuses it — never re-implement the
  colour mapping inline elsewhere (this matches the tiers defined in `ARCHITECTURE.md`
  Section 4 — keep them in sync).
- **Tailwind only, no inline `style={{}}` unless truly dynamic** (e.g., a chart's
  computed width). Keeps the visual language consistent across the whole dashboard.
- **Loading and error states are mandatory on every page that fetches data.** A judge
  watching a blank white screen while data loads looks broken — always show a loading
  skeleton or spinner, and a clear error message if the backend call fails.
- **Every screen that shows synthetic spares/maintenance data must carry a small,
  visible "illustrative data" label**, per the rule in `PROJECT_BRAIN.md` Section 2.

---

## 4. Visual design direction

- **Palette:** Navy/dark-blue base (defence/aviation feel), green/amber/red for the
  three health tiers, light neutral background — avoid a "startup consumer app" look;
  aim for a calm, professional, mission-ready dashboard tone.
- **Typography:** one clean sans-serif (e.g., Inter), large readable numbers for the
  fleet-availability percentage — that number is the single most important thing on
  the Fleet Overview page and should be the visual focal point.
- **Density:** this is a professional operations dashboard, not a marketing page — it's
  fine (good, even) to show a dense grid of aircraft cards rather than lots of empty
  whitespace, as long as each card is scannable at a glance.

---

## 5. How to run locally

```bash
cd frontend
npm install
cp .env.example .env.local      # then edit if backend runs on a different port/URL
npm run dev
```

Visit `http://localhost:5173` (Vite's default port).

---

## 6. Environment variables

| Variable | Purpose | Example |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL of the backend API | `http://localhost:8000` |

---

## 7. Adding a new page/component — checklist

1. Check `docs/API_CONTRACTS.md` for the exact data shape you'll receive.
2. Add any new API call to `src/lib/api.js` (don't call Axios elsewhere).
3. Build the component with a loading state, an error state, and the real-data state.
4. Reuse `StatusBadge.jsx` for any health-tier display — don't reinvent it.
5. If it displays synthetic data, add the "illustrative data" label.
