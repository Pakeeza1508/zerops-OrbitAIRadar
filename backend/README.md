# Orbit — AI Opportunity Radar Backend

FastAPI + MongoDB backend for Orbit. It discovers public student/developer opportunities, normalizes them, ranks them against a user profile, tracks deadlines, and preserves immutable snapshots when users save opportunities.

## What is implemented

- Email/password registration and login with Argon2 + JWT
- Student profile/onboarding persistence
- Opportunity listing, filtering, sorting, match score and eligibility output
- Opportunity detail with optional Groq match explanation
- Save/unsave plus immutable saved snapshots
- Saved statuses: `saved`, `planning`, `applied`; expired/master-deleted state is derived safely
- AI search: Groq when configured, deterministic fallback when not configured
- Live web discovery endpoint
- Public source registry with HTTP/RSS/sitemap/listing discovery
- Optional SearXNG discovery via `SEARXNG_BASE_URL`
- Deterministic extraction before AI: JSON-LD/meta/HTML/regex/date parsing
- Optional Crawl4AI rendered-page fallback (separate optional requirements file)
- Content hashing so unchanged pages skip Groq
- Deduplication by canonical URL and fingerprint
- Daily/manual ingestion pipeline with a singleton MongoDB lock
- Deadline/closed cleanup with saved snapshot preservation
- Ingestion run history and source-health endpoints
- `/health` and database-backed `/ready`
- Zerops daily cron definition

## Runtime

Python 3.11+ (3.12 recommended)

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Swagger docs: `http://localhost:8000/docs`

Health: `http://localhost:8000/health`

Readiness: `http://localhost:8000/ready`

## Required configuration

For local development, only MongoDB must be reachable. Groq and SearXNG are optional.

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=orbit
JWT_SECRET=<generate-a-long-random-secret>
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
SEARXNG_BASE_URL=
CORS_ORIGINS=http://localhost:3000
```

If `GROQ_API_KEY` is missing, deterministic parsing/matching/search remain available. If `SEARXNG_BASE_URL` is missing, the configured public source registry remains the primary discovery path.

## Daily job

```bash
python -m app.jobs.daily_sync
```

The same command is used by the Zerops cron job.

## Main API routes

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/profile`
- `PUT /api/profile`
- `GET /api/opportunities`
- `GET /api/opportunities/{id}`
- `POST /api/opportunities/{id}/save`
- `DELETE /api/opportunities/{id}/save`
- `GET /api/saved`
- `PATCH /api/saved/{saved_id}`
- `GET /api/stats`
- `POST /api/search/ai`
- `POST /api/search/live`
- `GET /api/ingestion/runs`
- `GET /api/ingestion/sources`
- `POST /api/ingestion/run`

See `API_CONTRACT.md` for details.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
python -m compileall -q .
```

## Optional Crawl4AI

The normal crawler does **not** require a browser. If you want rendered JavaScript-page fallback locally, install:

```bash
pip install -r requirements-crawl4ai.txt
```

Crawl4AI is imported lazily, so the backend still runs when it is not installed.

## Safety / crawler behavior

- Public HTTP(S) URLs only
- SSRF guard blocks private/loopback hosts
- robots.txt checked by the HTTP fetcher
- conservative per-domain delay
- no CAPTCHA bypass, login scraping, proxy rotation or bot-evasion logic
- official/primary source URLs are preferred

