# Orbit API Contract

All protected endpoints use:

```http
Authorization: Bearer <JWT>
```

## Authentication

### `POST /api/auth/register`

```json
{
  "email": "student@example.com",
  "password": "strong-password",
  "fullName": "Student Name"
}
```

Returns `accessToken` and user.

### `POST /api/auth/login`
Same shape minus `fullName`.

### `GET /api/auth/me`
Current authenticated user.

## Profile

### `GET /api/profile`

### `PUT /api/profile`

```json
{
  "fullName": "Student Name",
  "country": "Pakistan",
  "educationLevel": "undergraduate",
  "fieldOfStudy": "Computer Science",
  "institution": null,
  "graduationYear": 2027,
  "experienceLevel": "beginner",
  "skills": ["Python", "React", "AI"],
  "interests": ["Open Source"],
  "preferredCategories": ["internship", "fellowship", "open_source", "hackathon"],
  "locationPreference": ["remote", "global"],
  "preferredCountries": [],
  "fundingPreference": "funded_only"
}
```

## Opportunities

### `GET /api/opportunities`

Supported query parameters:

- `q`
- `category` comma-separated
- `remote=true|false`
- `funded=true|false`
- `deadlineBefore=<ISO datetime>`
- `deadlineAfter=<ISO datetime>`
- `countries` comma-separated
- `education` comma-separated
- `skills` comma-separated
- `minMatch=0..100`
- `sort=best_match|newest|deadline`
- `page`
- `pageSize`
- `includeUnverified`

Each item contains factual opportunity data plus user-specific:

- `matchScore`
- `eligibilityStatus`
- `matchedSkills`
- `missingSkills`
- `matchingReasons`
- `daysRemaining`
- `applyUrl`

### `GET /api/opportunities/{id}?explainAI=true`
Returns detail; optional Groq explanation when configured.

## Dashboard

### `GET /api/stats`

Returns:

```json
{
  "recommended": 12,
  "closingSoon": 3,
  "newToday": 4,
  "saved": 5,
  "totalActive": 42
}
```

## Saved

### `POST /api/opportunities/{id}/save`
Creates/refreshes an immutable factual snapshot.

### `DELETE /api/opportunities/{id}/save`

### `GET /api/saved`
Returns saved rows; `expired=true` if its deadline passed or the master record was removed.

### `PATCH /api/saved/{saved_id}`

```json
{
  "applicationStatus": "planning",
  "notes": "Prepare proposal this week."
}
```

Status values: `saved`, `planning`, `applied`.

## Search

### `POST /api/search/ai`

```json
{
  "query": "Fully funded remote AI internships for Pakistani undergraduate students"
}
```

Groq converts the request to an allow-listed Pydantic filter structure when configured. Without Groq, a deterministic parser is used.

### `POST /api/search/live`

```json
{
  "query": "open source mentorship applications",
  "maxResults": 12
}
```

Runs discovery, then returns newly available matching records. SearXNG adds broader search candidates only when configured.

## Ingestion

### `POST /api/ingestion/run`

```json
{
  "query": null,
  "maxCandidates": 30
}
```

Returns immediately with a run id and schedules the ingestion in FastAPI background tasks.

### `GET /api/ingestion/runs`
### `GET /api/ingestion/runs/{id}`
### `GET /api/ingestion/sources`
### `POST /api/ingestion/seed-sources`

Run fields include:

- sources attempted/succeeded
- URLs discovered/fetched
- new/updated/duplicate/expired/failed counts
- AI calls
- status and errors

