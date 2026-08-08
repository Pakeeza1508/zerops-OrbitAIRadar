# Orbit Backend — Zerops Deployment

This file covers the FastAPI backend service. The final repository can later use one root `zerops.yaml` for both React + API; the included backend `zerops.yaml` is valid when this backend directory is the deployment working directory.

## Service

Create a Python runtime service named/setup as `api`.

The included configuration uses:

- Python 3.12
- port 8000 with HTTP support
- Uvicorn/FastAPI start command
- `/ready` as deployment readiness check
- `/health` as runtime health check
- one daily cron job at 02:00 UTC

## Runtime environment variables

Add these to the **API service only**:

```env
MONGO_URL=<your MongoDB Atlas URI>
DB_NAME=orbit
JWT_SECRET=<long random secret>
CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN

GROQ_API_KEY=<add later>
GROQ_MODEL=openai/gpt-oss-20b
SEARXNG_BASE_URL=<optional self-hosted URL>

MAX_AI_CALLS_PER_SYNC=100
MAX_CANDIDATES_PER_RUN=80
MAX_URLS_PER_SOURCE=20
DELETE_EXPIRED_MASTER=true
ALLOW_USER_MANUAL_INGESTION=true
```

Do not expose `MONGO_URL`, `JWT_SECRET`, or `GROQ_API_KEY` to React.

## Daily cron

The included `zerops.yaml` runs:

```bash
python3 -m app.jobs.daily_sync
```

with:

```text
0 2 * * *
```

and `allContainers: false`, so a horizontally scaled API does not run duplicate daily jobs.

## Deploy

When deploying this backend directory directly:

```bash
zcli service push api
```

If this folder is nested in a monorepo, use the Zerops CLI working-directory / YAML-path options or move the final multi-service `zerops.yaml` to repository root.

## Verification after deployment

1. Open `/health`.
2. Open `/ready`; it should be HTTP 200 and show MongoDB connected.
3. Open `/docs`.
4. Register a user.
5. Save a complete profile.
6. Run `POST /api/ingestion/run`.
7. Poll `/api/ingestion/runs/{id}`.
8. Confirm `/api/opportunities` contains normalized records.
9. Add your Groq key and test `/api/search/ai`.
10. Add SearXNG later and test `/api/search/live` for broader discovery.

## Crawl4AI on Zerops

Crawl4AI is intentionally optional because browser dependencies increase deployment size and memory. Start with the default HTTP/BeautifulSoup crawler. If live pages prove that JavaScript rendering is required, install `requirements-crawl4ai.txt` and add the corresponding browser/runtime system dependencies in the Zerops Python runtime preparation step.

