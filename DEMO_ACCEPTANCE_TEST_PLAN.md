# Orbit AI Radar — Demo acceptance test plan (2026-11-23)

## Deployment scope and safety
- Feature branch: `fix/orbit-demo-readiness` based on `deployment/vercel-mvp`.
- Main and production branches remain untouched; do not merge/promote before acceptance.
- Use preview FRONTEND and preview BACKEND belonging to the SAME branch; confirm `REACT_APP_BACKEND_URL` points to the expected preview backend and CORS permits the frontend origin. Vercel production environment variables are not automatically equivalent to preview values.
- Use an isolated test account. Do not post JWTs, passwords, database URLs or Groq keys in reports.
- Do not trigger manual crawling, delete opportunity documents or modify MongoDB master records.
- No synthetic opportunities or invented deadlines. Historical database data is not a verified live index.

## Must-pass demo flow
| ID | Action | Expected |
|---|---|---|
| A1 | Open preview landing page, log in | Backend login succeeds; no CORS, HTTP 500 or redirect loop |
| A2 | Refresh, then logout, then log in again | Auth session restored when expected; protected pages guarded |
| A3 | Update profile (country Pakistan, undergraduate, Python/AI skills) | Save succeeds and persists across refresh and re-login |
| B1 | Open dashboard | Real indexed records appear; initial loading does not flash misleading 0 |
| B2 | Open Discover, use category filter | Backend-filtered subset returned; filters indicator accurate |
| B3 | Ask Orbit: "Find fully funded AI research fellowships for undergraduate students in Pakistan" | AI API request fires once; main results count/cards reflect returned `items`, not previous 36; "AI interpreted" or "Rule-based fallback" and parsed filters are displayed truthfully |
| B4 | Ask Orbit: "Find fully funded undergraduate AI internships in Antarctica closing tomorrow" | If API returns 0, main list shows 0 and proper no-results message; previous results must not reappear |
| B5 | Clear AI search | Original Discover list returns |
| B6 | Change manual filter or text search after AI query | AI results cleared; normal server-side pagination/filter mode restored |
| B7 | Inspect 4 indexed cards including historical FAQ/title | Obvious FAQ/news/closeout pages excluded by backend hygiene if preview backend used; unknown dates shown as "Deadline not stated", never "null days left"; HTML entities decoded |
| C1 | Save genuine opportunity, visit Saved, switch to Planning, reload, unsave | Saved snapshot and status persisted; test user cleanup complete |
| C2 | Open opportunity details, click external official source | Link opens intended origin; no application submitted |
| D1 | Open Radar | Last confirmed run date shown; stale scan not called live |
| D2 | Inspect sources and run details | Enabled/URL (where available), status, available counters shown; unavailable metrics labelled N/A |
| D3 | Verify non-admin account | Manual run permission not offered; no crawl triggered |
| E1 | Vercel backend logs after AI search | HTTP 200 and no new Groq 401; verify `usedAI` in API payload to confirm AI success, not just key presence |
| E2 | Browser network and console | No unhandled errors, HTTP 500 or CORS. Record timings of load and search |

## Test evidence to collect
For each step: PASS/FAIL/NOT TESTED, preview URL, screenshot or request status if failure, response `total`, `usedAI` and `filters` (do not copy tokens), and relevant browser console errors.

## Known limitations — not "fixed" by demo UI patch
- Historical indexed opportunities may still have missing deadlines and eligibility and should not be described as verified/open.
- Read-time rejection of obviously generic page titles is deliberately conservative; it does not replace an ingestion validation redesign or clean the DB.
- Backend parser may still mishandle complex nationality, education and deadlines; displayed parsed filters make this visible, not automatically correct.
- Autonomous recurring crawler scheduling and long-running crawling on Vercel are not implemented/verified.
- Cold starts and Mongo index initialization can impact latency.
- Initial Vercel production URL is not the preview. Promote only after testing and explicit decision.

## Acceptance / release rule
Do NOT promote to production if B3/B4/B5, A1/A3 or C1 fails. Record any unsupported eligibility search as a limitation; do not demonstrate it as guaranteed matching. Verify source page and current application status before describing an opportunity as open.
