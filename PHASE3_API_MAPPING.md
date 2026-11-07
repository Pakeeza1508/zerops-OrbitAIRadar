# Phase 3 frontend ↔ FastAPI contract and preservation audit

Baseline: main @ d786949e9c57 (Phase 2 merged). The Phase 3 branch is isolated from main.

## Contract mapping (verified against backend/API_CONTRACT.md and backend route/service code)

| Frontend current | Backend source | Phase 3 binding |
|---|---|---|
| numeric `opportunity.match` | `matchScore` numeric, `match` object | numeric UI `match = matchScore`, keep object separately if needed |
| `applicationUrl` | `applyUrl` fallback; `applicationUrl` original | prefer `applyUrl || applicationUrl` |
| `opportunity.id` | Mongo serialized `id` | preserve id string |
| `matchedSkills`, `requirements` etc. | backend optional or differently named | normalize arrays to safe [] and preserve factual values |
| `opportunity.verified` | backend record status/source verification | derive only from explicit source metadata; never invent verification |
| `opportunity.daysRemaining` | number or null | handle no deadline separately |
| local saved `status` | `applicationStatus` = saved/planning/applied | normalize to UI status; expired is computed server flag, NOT mutable applicationStatus |
| local saved keyed by opportunity id | `GET /api/saved` returns rows: id, originalOpportunityId, snapshot, applicationStatus, expired | key by originalOpportunityId; PATCH uses saved row id |
| saved toggle localStorage `orbit_saved` | POST/DELETE `/api/opportunities/{id}/save` | remove localStorage writes entirely |
| stats computed from local seed | GET `/api/stats`: recommended, closingSoon, newToday, saved, totalActive | use API stats and matching threshold shown in labels |
| keyword `askOrbit` simulation | POST `/api/search/ai` `{query}` -> `{answer, filters, items, total, usedAI, aiConfigured}` | render response; no local keyword filtering |
| local search sort: Best match/Newest/Deadline soon | `sort=best_match|newest|deadline` | map; API does sorting |
| filters local workMode/funding | API `remote` boolean and `funded` boolean | Remote and funded flags map directly; Hybrid/on-site and individual funding kinds have no exact backend query parameter |
| local deadline presets | API `deadlineBefore` ISO datetime | convert presets to ISO dates |
| results array local | `GET /api/opportunities` returns `{items,total,page,pageSize}` | never infer no records from failed network; explicit error and empty state |

## Important mismatches

1. Backend `match` is an OBJECT, unlike numeric UI `match`. Incorrect direct mapping breaks ranking and percentages.
2. Backend saved PATCH endpoint uses the SAVED ROW ID, while toggling save uses the OPPORTUNITY ID.
3. Expired is computed by backend and cannot be set via `applicationStatus`.
4. Backend `sort=best_match` computes a per-user score; no client-side seed sorting is authoritative.
5. Backend filters support a boolean remote/funded, not exact Hybrid, On-site, Paid/Prize funding kinds; avoid pretending unsupported filters are server-exact.
6. Groq is optional. `/api/search/ai` can use deterministic backend fallback, but is never the old browser keyword simulation.

## Existing search/content-delivery pipeline: preserve

The FastAPI `/api/search/live` and `/api/ingestion/*` routes, scraping pipeline, scheduler, content source collection and deployment environment are OUT OF SCOPE. Do not remove, disable, edit or trigger them in Phase 3. Frontend fake live-search and fake ingestion results are NOT the backend pipeline: disable misleading demo controls instead of connecting them to ingestion. Do not touch `zerops.yaml`, backend scheduler or crawler configuration. Existing content updates continue through backend processes independently of frontend read integration.

Phase 3 branch must stay unmerged until approval. Release/deployment is Phase 5.
