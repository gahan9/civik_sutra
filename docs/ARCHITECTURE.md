# Architecture

CivikSutra is one **React** SPA (`frontend/`) and one **FastAPI** app (`functions/`). Two **supported** deployment topologies share the same code: **(1) Firebase** (Hosting + Cloud Functions + Firestore) and **(2) Cloud Run** (SPA + API images from [cloudbuild.yaml](../cloudbuild.yaml), Firestore when wired). The README **Architecture** table summarizes paths A and B.

## Deployment topology (unified)

```
                    ┌───────────────────────────────────┐
                    │  Browser (PWA)                    │
                    └──────────────────┬──────────────────┘
                                       │ HTTPS
                    ┌──────────────────▼──────────────────┐
                    │  Static: Firebase Hosting or        │
                    │  Cloud Run civiksutra-web           │
                    └──────────────────┬──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │  API: Cloud Functions or            │
                    │  Cloud Run civiksutra-api (FastAPI) │
                    └──────────┬─────────────┬────────────┘
                               │             │
              ┌────────────────┼─────────────┼────────────────┐
    ┌─────────▼──────┐ ┌───────▼───────┐ ┌───▼──────────────┐
    │ Firestore      │ │ Secrets        │ │ Gemini, Vertex,  │
    │ cache / limits │ │                │ │ Translation, Maps│
    └────────────────┘ └────────────────┘ └──────────────────┘
```

## Why monolithic Firebase (path 1)

| Concern | Firebase Answer |
|---------|----------------|
| Deploy complexity | `firebase deploy` -- one command ships everything |
| Database | Firestore with offline support, real-time sync, automatic scaling |
| Auth | Firebase Auth (anonymous) -- no signup wall for civic app |
| CDN | Firebase Hosting is backed by global CDN |
| Functions | Cloud Functions scale to zero, pay-per-invocation |
| Local dev | Firebase Emulator Suite runs everything locally |
| Cost | Spark (free) plan covers prototype; Blaze (pay-as-you-go) for production |

### Cloud Run (path 2)

| Concern | Cloud Run + Cloud Build answer |
|---------|-------------------------------|
| Build | `gcloud builds submit --config=cloudbuild.yaml` runs tests, builds `Dockerfile` + `Dockerfile.api`, pushes to Artifact Registry |
| Serve | Two services: static nginx (`civiksutra-web`) and API (`civiksutra-api`); map custom domains in Cloud Run |
| Parity | Same `functions` Python and `frontend` dist as local emulators; configure API base URL in the SPA build |

## Data Flow

### Booth Finder Flow

```
User (mobile browser)
  │
  ├─ GPS: navigator.geolocation.getCurrentPosition()
  │
  ▼
Frontend (React)
  │
  ├─ POST /booth/nearby { lat, lng, radius_km }
  │
  ▼
Cloud Function: booth_nearby()
  │
  ├─ Check Firestore cache (key: geohash prefix)
  │   ├─ HIT: return cached booths
  │   └─ MISS:
  │       ├─ Google Maps Places API: nearby polling stations
  │       ├─ Google Maps Directions API: distance/duration for top N
  │       ├─ Store in Firestore with TTL (7 days)
  │       └─ Return results
  │
  ▼
Frontend renders map with booth markers
  │
  ├─ User taps booth
  ├─ POST /booth/directions { origin, destination, mode }
  │
  ▼
Cloud Function: booth_directions()
  │
  ├─ Google Maps Directions API (with departure_time for traffic)
  ├─ Return: steps, duration, duration_in_traffic, polyline
  │
  ▼
Frontend renders route on map + traffic-aware timing advice
```

### Candidate Intelligence Flow

```
User selects constituency (from GPS or manual input)
  │
  ├─ POST /candidate/search { constituency | lat,lng }
  │
  ▼
Cloud Function: candidate_search()
  │
  ├─ Check Firestore cache (key: constituency_name)
  │   ├─ HIT (< 24h): return cached
  │   └─ MISS:
  │       ├─ ScraperService: fetch MyNeta candidate list
  │       ├─ Parse: name, party, education, criminal_cases, assets
  │       ├─ Store in Firestore with TTL (24h)
  │       └─ Return candidate list
  │
  ▼
User selects 2-4 candidates for comparison
  │
  ├─ POST /candidate/compare { candidate_ids }
  │
  ▼
Cloud Function: candidate_compare()
  │
  ├─ For each candidate:
  │   ├─ Firestore: get cached profile
  │   ├─ CandidateService.grounding_search(name):
  │   │   └─ Gemini API with Google Search grounding
  │   │   └─ Returns: recent news, achievements, controversies
  │   └─ CandidateService.background_check(id):
  │       └─ Structured extraction from MyNeta + grounding
  │
  ├─ Build comparison matrix:
  │   ┌──────────────┬──────────────┬──────────────┐
  │   │ Dimension    │ Candidate A  │ Candidate B  │
  │   ├──────────────┼──────────────┼──────────────┤
  │   │ Education    │ MBA, IIT     │ BA, State U  │
  │   │ Criminal     │ 0 cases      │ 2 cases      │
  │   │ Assets       │ ₹2.1 Cr     │ ₹45 Cr       │
  │   │ Past Work    │ MLA 2 terms  │ First time   │
  │   │ Key Promises │ ...          │ ...          │
  │   │ News (30d)   │ ...          │ ...          │
  │   └──────────────┴──────────────┴──────────────┘
  │
  ▼
Frontend renders comparison table
```

### Assistant Chat Flow

```
User types question in chat UI
  │
  ├─ POST /assistant/chat { message, session_id, language }
  │   (Server-Sent Events for streaming)
  │
  ▼
Cloud Function: assistant_chat()
  │
  ├─ Load conversation history from Firestore (session_id)
  ├─ Build Gemini request:
  │   ├─ System prompt: election education expert
  │   ├─ Tools: [booth_finder, candidate_search, verify_voter]
  │   ├─ Grounding: Google Search enabled
  │   ├─ Safety settings: explicit configuration
  │   └─ Language: respond in user's preferred language
  │
  ├─ Gemini processes:
  │   ├─ If tool call needed:
  │   │   ├─ Execute tool (GeoService / CandidateService)
  │   │   ├─ Feed result back to Gemini
  │   │   └─ Continue generation
  │   └─ Stream response tokens
  │
  ├─ Save updated conversation to Firestore
  │
  ▼
Frontend renders streamed response with citations
```

## Firestore Schema

```
firestore/
├── booths/
│   └── {geohash_prefix}/
│       ├── name: string
│       ├── address: string
│       ├── location: GeoPoint
│       ├── constituency: string
│       ├── facilities: string[]        # wheelchair, braille, etc.
│       ├── fetched_at: timestamp       # for TTL (7 days)
│       └── source: string             # "google_maps" | "eci"
│
├── candidates/
│   └── {constituency_slug}/
│       └── {candidate_id}/
│           ├── name: string
│           ├── party: string
│           ├── party_symbol: string
│           ├── education: string
│           ├── age: number
│           ├── criminal_cases: number
│           ├── criminal_details: string[]
│           ├── total_assets: number
│           ├── total_liabilities: number
│           ├── past_positions: string[]
│           ├── grounding_summary: string
│           ├── fetched_at: timestamp   # TTL (24h)
│           └── source: string
│
├── manifestos/
│   └── {party_slug}/
│       ├── party_name: string
│       ├── election_year: number
│       ├── categories: map
│       │   ├── economy: string
│       │   ├── education: string
│       │   ├── healthcare: string
│       │   ├── infrastructure: string
│       │   ├── defense: string
│       │   └── social_welfare: string
│       ├── full_text_url: string
│       ├── summary: string             # Gemini-generated
│       └── fetched_at: timestamp       # TTL (7 days)
│
├── sessions/
│   └── {session_id}/
│       ├── created_at: timestamp
│       ├── language: string
│       ├── location: GeoPoint | null
│       ├── messages: array
│       │   └── { role, content, timestamp, citations? }
│       └── request_count: number       # for rate limiting
│
└── rate_limits/
    └── {ip_hash}/
        ├── gemini_requests: number
        ├── vision_calls: number
        ├── window_start: timestamp     # resets daily
        └── last_request: timestamp
```

## Security Model

```
                        ┌─────────────────────┐
                        │  reCAPTCHA v3        │
                        │  Score >= 0.5        │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Firebase Auth       │
                        │  (Anonymous)         │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Rate Limiter        │
                        │  100 Gemini/day      │
                        │  50 Vision/day       │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Input Validation    │
                        │  Pydantic models     │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Business Logic      │
                        └──────────────────────┘
```

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Booths and candidates: read-only from client
    match /booths/{doc=**} {
      allow read: if true;
      allow write: if false;  // only Cloud Functions write
    }
    match /candidates/{doc=**} {
      allow read: if true;
      allow write: if false;
    }
    match /manifestos/{doc=**} {
      allow read: if true;
      allow write: if false;
    }
    // Sessions: user can read own session only
    match /sessions/{sessionId} {
      allow read: if request.auth != null
                  && request.auth.uid == resource.data.uid;
      allow write: if false;  // only Cloud Functions write
    }
    // Rate limits: no client access
    match /rate_limits/{doc} {
      allow read, write: if false;
    }
  }
}
```

## API Surface

All endpoints are Firebase HTTPS Cloud Functions. Single deployment unit.

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| POST | `/booth/nearby` | `{ lat, lng, radius_km }` | `BoothResult[]` | anon |
| POST | `/booth/directions` | `{ origin, destination, mode }` | `DirectionsResult` | anon |
| GET | `/booth/verify/{epic}` | - | `{ redirect_url, instructions }` | anon |
| POST | `/candidate/search` | `{ constituency? lat? lng? }` | `CandidateSummary[]` | anon |
| GET | `/candidate/{id}/background` | - | `BackgroundReport` | anon |
| POST | `/candidate/compare` | `{ candidate_ids: string[] }` | `ComparisonMatrix` | anon |
| POST | `/manifesto/compare` | `{ party_names: string[] }` | `ManifestoComparison` | anon |
| POST | `/assistant/chat` | `{ message, session_id, lang }` | SSE stream | anon + reCAPTCHA |

## External API Dependencies

| API | Purpose | Quota (daily) | Fallback |
|-----|---------|---------------|----------|
| Google Maps JavaScript | Map rendering | Client-side, no server cost | Leaflet + OSM |
| Google Maps Directions | Route + traffic | 2,500 free elements | Cached routes |
| Google Maps Places | Booth search | 5,000 free requests | Pre-seeded Firestore |
| Gemini 2.0 Flash | Chat, grounding, analysis | 100 requests (`.env`) | Cached responses |
| Vision API | Affidavit OCR (future) | 50 calls (`.env`) | Manual data entry |
| reCAPTCHA v3 | Bot protection | Unlimited (free tier) | None needed |
