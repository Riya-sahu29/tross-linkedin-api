# LinkedIn Profile API

A FastAPI service that accepts a public LinkedIn profile URL and returns structured profile data as JSON: name, headline, location, about, experience, education, skills, certifications, languages, and profile images (where available).

# LinkedIn Profile API

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.9-E92063?logo=pydantic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)
![Apify](https://img.shields.io/badge/Data%20via-Apify-FF9012?logo=apify&logoColor=white)

A FastAPI service that accepts a public LinkedIn profile URL and returns structured profile data as JSON: name, headline, location, about, experience, education, skills, certifications, languages, and profile images (where available).

## Live deployment

`POST https://<your-render-app>.onrender.com/profile`
## Live deployment

`POST https://<your-render-app>.onrender.com/profile`

## Approach

Client
│ POST /profile { "linkedin_url": "..." }
▼
FastAPI (app/main.py)
│ URL validation, error handling, OpenAPI docs at /docs
▼
ApifyClient (app/services/apify_client.py)
│ Calls a managed, no-login LinkedIn scraping provider (Apify)
▼
Normalizer (app/services/normalizer.py)
│ Maps provider-specific field names into a stable schema
▼
ProfileResponse (app/schemas.py, Pydantic)
▼
JSON


**Why a third-party provider (Apify) instead of hitting LinkedIn's endpoints directly with my own account:**

LinkedIn's User Agreement prohibits scraping and automated data collection, and logging in with a personal account to hit private, undocumented endpoints risks that account being banned — LinkedIn has also pursued legal action against scraping services in the past (e.g. the *hiQ Labs v. LinkedIn* litigation). Publishing that kind of credential-based scraper in a public repository under my own name compounds that risk indefinitely.

Instead, this service delegates the actual data extraction to a managed provider (Apify's LinkedIn Profile Scraper) that operates on its own infrastructure without requiring my LinkedIn login or session cookies. This keeps the architecture, API design, validation, error handling, and deployment — the parts of the challenge that are actually about backend engineering — as the focus, while avoiding building and open-sourcing a personal-account credential scraper.

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd tross-linkedin-api
pip install -r requirements.txt
```

### 2. Get an Apify API token (free)

1. Sign up at https://console.apify.com (free tier, no card required)
2. Go to **Settings → API & Integrations** and copy your API token
3. Apify's free plan includes monthly usage credits, enough for testing this challenge

### 3. Configure environment

```bash
cp .env.example .env
# then edit .env and paste your APIFY_API_TOKEN
```

### 4. Run locally

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs.

### 5. Test it

```bash
curl -X POST http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{"linkedin_url": "https://www.linkedin.com/in/someone"}'
```

## API documentation

### `POST /profile`

**Request body**

```json
{ "linkedin_url": "https://www.linkedin.com/in/someone" }
```

**Response `200`**

```json
{
  "source_url": "https://www.linkedin.com/in/someone",
  "name": "Jane Doe",
  "headline": "Software Engineer at Acme",
  "location": "Bengaluru, India",
  "about": "...",
  "profile_image_url": "https://...",
  "banner_image_url": null,
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Acme",
      "location": null,
      "start_date": "2023",
      "end_date": "Present",
      "duration": null,
      "description": null
    }
  ],
  "education": [...],
  "skills": ["Python", "FastAPI"],
  "certifications": [...],
  "languages": [{ "name": "English", "proficiency": null }],
  "raw_fields_available": []
}
```

**Errors**

| Status | Meaning |
|---|---|
| 422 | `linkedin_url` is missing or not a valid `linkedin.com/in/...` URL |
| 401 | Missing/invalid `X-API-Key` header (only if `SERVICE_API_KEY` is set) |
| 502 | The upstream provider failed, timed out, or returned no data (private/deleted profile, quota exhausted, etc.) |

### `GET /health`

Liveness check, returns `{"status": "ok"}`.

Full interactive schema is always available at `/docs` (Swagger) and `/redoc`.

## Deployment (Render, free tier)

1. Push this repo to GitHub
2. On [Render](https://render.com), create a **New Web Service** from the repo
3. Render detects the `Dockerfile` automatically — no build command needed
4. Add environment variable `APIFY_API_TOKEN` in the Render dashboard under **Environment**
5. Deploy — Render provides an HTTPS URL automatically

## Known limitations

- **Coverage depends on the Apify actor's success rate.** LinkedIn actively changes its markup and anti-bot defenses; a field that's populated today may come back empty next week if the underlying actor hasn't been updated. `raw_fields_available` in the response surfaces any provider fields the normalizer didn't map, for debugging.
- **No certifications/languages on many profiles.** These sections are often private by default on LinkedIn, so empty arrays are expected and not necessarily a bug.
- **Rate limits / cost.** The free Apify tier includes limited monthly credits; heavy use will need a paid plan.
- **This is not a general LinkedIn search/scrape tool.** It accepts one public profile URL per request and does not support bulk lookups, company pages, or authenticated/private data.
- **No caching layer.** Every request re-runs the underlying actor; a production version would add a cache (e.g. Redis) keyed on profile URL with a TTL to reduce cost and latency.
- **No automated test suite included** given the timeline — validator and normalizer logic were manually verified against sample payloads, but a real submission would add `pytest` coverage.

## Project structure
app/
├── main.py # FastAPI app, routes, request validation
├── config.py # Environment-based settings
├── schemas.py # Pydantic response models
├── services/
│ ├── apify_client.py # Calls the Apify actor
│ └── normalizer.py # Maps raw provider output → schema
└── utils/
└── validators.py # LinkedIn URL validation
