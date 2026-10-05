# DEPLOYMENT.md — AirReady

Read `BACKEND.md` and `FRONTEND.md` first — this assumes both run locally already.

Goal: get a live URL you can open on a judge's laptop/projector without running
anything locally during the demo (and a local fallback in case wifi fails — see
`TESTING.md`).

---

## 1. Recommended setup (both free-tier friendly)

- **Backend → Render** (Web Service, free tier is fine for a demo)
- **Frontend → Vercel** (static site / Vite build, free tier)

These are suggestions, not requirements — Railway, Fly.io, or Netlify work equally
well if your team already has accounts there. The steps below are for Render + Vercel.

---

## 2. Deploy the backend (Render)

1. Push your repo to GitHub first (see the root `README.md` / main setup guide for
   `git init` steps if not done yet).
2. Go to Render → New → Web Service → connect your GitHub repo.
3. Set:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (from `backend/.env.example`) in Render's dashboard:
   - `MODEL_PATH` → note that on Render, the model file needs to be committed to the
     repo (or fetched on build) since there's no persistent local `ml/` folder
     relationship the way there is locally — simplest fix: copy `ml/models/rul_model.pkl`
     into `backend/app/model_artifact/rul_model.pkl` before deploying, and point
     `MODEL_PATH` there.
   - `CORS_ORIGINS` → set to your Vercel frontend URL once you have it (step 3 below),
     e.g. `https://airready.vercel.app`.
5. Deploy. Confirm `https://<your-render-url>/health` returns `{"status": "ok"}` and
   `https://<your-render-url>/docs` shows the live API docs.

---

## 3. Deploy the frontend (Vercel)

1. Go to Vercel → New Project → import your GitHub repo.
2. Set:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Add environment variable:
   - `VITE_API_BASE_URL` → your Render backend URL from step 2.
4. Deploy. Visit the generated Vercel URL and confirm the Fleet Overview page loads
   real data from the backend (open browser dev tools → Network tab if it doesn't,
   and check for a CORS error — if so, double check `CORS_ORIGINS` on Render matches
   this exact Vercel URL).

---

## 4. Order matters

Deploy the **backend first**, get its live URL, *then* set `VITE_API_BASE_URL` on
the frontend and deploy it. Deploying frontend first just means one redeploy later
once you have the backend URL — not a big deal, but doing backend first avoids it.

---

## 5. Demo-day fallback plan

Live internet at a venue is not always reliable. Before the demo:

1. Confirm the full flow also works with both servers running **locally**
   (`uvicorn ... --reload` + `npm run dev`), as a fallback if the live URLs are
   unreachable on venue wifi.
2. Take screenshots/screen-recording of the working dashboard as an absolute last
   resort fallback (see `TESTING.md` Section 4).
3. Pre-load the Fleet Overview page in a browser tab **before** you're called up, so
   it's not trying to cold-load during your limited presentation time.
