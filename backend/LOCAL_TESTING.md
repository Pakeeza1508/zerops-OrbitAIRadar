# Orbit Backend — Local Testing Guide

## 1. Prerequisites

Install:

- Python 3.12 (recommended)
- MongoDB locally **or** a MongoDB Atlas connection string

Groq and SearXNG are optional during the first local boot.

## 2. Create environment

From the backend folder:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 3. Configure `.env`

Copy `.env.example` to `.env`.

Minimum local configuration:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=orbit
JWT_SECRET=replace-with-a-long-random-secret
CORS_ORIGINS=http://localhost:3000
```

### Add Groq later

When ready for live AI tests:

```env
GROQ_API_KEY=YOUR_KEY_HERE
GROQ_MODEL=openai/gpt-oss-20b
```

The key belongs **only in the backend `.env`**, never in React.

### Add SearXNG later

```env
SEARXNG_BASE_URL=http://localhost:8080
```

If omitted, source-registry crawling still works.

## 4. Start backend

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Verify:

```text
GET http://localhost:8000/health
GET http://localhost:8000/ready
GET http://localhost:8000/docs
```

`/ready` should return HTTP 200 only when MongoDB is reachable.

## 5. Core test flow

Use Swagger at `/docs`, Postman, or curl.

1. `POST /api/auth/register`
2. Copy returned `accessToken`
3. Add `Authorization: Bearer <token>`
4. `PUT /api/profile`
5. `POST /api/ingestion/run`
6. Poll `GET /api/ingestion/runs/{id}`
7. `GET /api/opportunities?sort=best_match`
8. Open `GET /api/opportunities/{id}`
9. `POST /api/opportunities/{id}/save`
10. `GET /api/saved`
11. `POST /api/search/ai`
12. If SearXNG is configured, test `POST /api/search/live`

## 6. Run a full discovery job directly

```bash
python -m app.jobs.daily_sync
```

It should print a JSON run result.

The job:

- loads enabled sources
- discovers URLs
- fetches public pages
- rejects generic listing/index pages as final opportunity cards
- runs deterministic extraction first
- calls Groq only for ambiguous/incomplete pages when configured
- skips AI on unchanged content hashes
- deduplicates/upserts opportunities
- expires dead opportunities
- preserves independent user snapshots
- stores run statistics

## 7. Verify saved-snapshot lifecycle

1. Save an active opportunity.
2. Inspect `saved_opportunities` in MongoDB: it must contain a full `snapshot`.
3. Set the master opportunity deadline to a past UTC date.
4. Run `python -m app.jobs.daily_sync` or invoke cleanup through an ingestion run.
5. The master may be removed when `DELETE_EXPIRED_MASTER=true`.
6. The saved row must remain, with `masterDeleted=true`; `GET /api/saved` should report it as expired.

## 8. Test AI graceful degradation

Remove/comment `GROQ_API_KEY` and restart.

Expected:

- backend still boots
- normal crawling works
- deterministic matching works
- `/api/search/ai` falls back to deterministic natural-language parsing
- `explainAI=true` simply has no generated explanation if Groq is unavailable

## 9. Test SearXNG graceful degradation

Remove/comment `SEARXNG_BASE_URL` and restart.

Expected:

- source-registry crawler still runs
- SearXNG searches return no external candidates rather than crashing the app

## 10. Automated tests

```bash
pytest -q
python -m compileall -q .
```

## 11. Connect the React frontend

Frontend environment:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

Never copy `GROQ_API_KEY`, `JWT_SECRET`, or MongoDB credentials to the frontend.

