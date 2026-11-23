# Orbit — Vercel deployment experiment

Branch: `deployment/vercel-mvp`. The `main` branch and application/crawling logic remain unchanged.

## Architecture
Use **two separate Vercel projects** connected to this same GitHub repo and this branch:

1. **orbit-api** — Root Directory: `backend`; Python / FastAPI auto-detection; `backend/server.py` exports `app`.
2. **orbit-web** — Root Directory: `frontend`; Create React App build (install `npm install --legacy-peer-deps`, build `npm run build`, output `build`). Existing SPA rewrites live in `frontend/vercel.json`.

## API environment variables (Vercel dashboard, server-side only)
- `MONGODB_URI` (or `MONGO_URL`) — production Atlas connection URI
- `DB_NAME` — `orbit`
- `JWT_SECRET` — a new long, random production secret
- `GROQ_API_KEY` — API key, required for Groq-powered AI
- `CORS_ORIGINS` — exact HTTPS URL of the deployed frontend (no trailing slash)
- `ADMIN_EMAIL` — optional, only if needed for admin ingestion controls
- Other crawler settings — use existing defaults initially

Do not store real credentials in GitHub or in frontend variables. Use a separate production MongoDB database or cluster for testing, or ensure you have a backup of production data before seeding or ingesting.

## Frontend environment variables
Set `REACT_APP_BACKEND_URL` to the **exact HTTPS API Vercel URL** (no trailing slash). It must override the repository's local `frontend/.env` value during Vercel build. After setting it, redeploy the frontend.

## Deployment sequence
1. Import GitHub repository as an API project with Root Directory `backend`. Deploy branch `deployment/vercel-mvp` as a preview; create production deployment only when ready.
2. Add API secrets to the correct deployment environment. Redeploy.
3. Verify API `/health` and `/ready`; `/ready` must return HTTP 200 and MongoDB connected.
4. Import the same repository as frontend project with Root Directory `frontend`. Set `REACT_APP_BACKEND_URL` to API URL.
5. Set API `CORS_ORIGINS` to exact frontend domain and redeploy API.
6. Test registration, login, profile persistence, opportunity loading, save/unsave and AI search end to end.
7. Check API logs for startup failures, MongoDB DNS errors, timeouts, memory and request duration.

## Scope and limitations
This experiment deploys the existing HTTP API. It does **not** automatically schedule the existing `python -m app.jobs.daily_sync` crawler. Vercel Functions are request-driven and bounded by execution time. Triggered manual ingestion may time out if the pipeline is long; verify it cautiously with restricted data and authorized endpoints.

If ingestion requires heavy browsers (Playwright/Crawl4AI), it may exceed packaging/resource limits. The app can be hosted on Vercel while the unchanged discovery job later runs separately via an authorized scheduler. Do not claim continuous crawling until it is verified.

No code has been modified in the frontend, API endpoints, or crawling modules for this deployment experiment.
