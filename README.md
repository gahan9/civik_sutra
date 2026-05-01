# Election Process Education Assistant

**Prompt Wars Challenge 2** -- An AI-powered assistant that helps voters understand the election process, find their polling booth, research candidates, and make informed decisions.

## What This Does

A mobile-first web application that meets voters where they are -- physically and informationally. Uses GPS to find nearby booths, Gemini AI for candidate research with Google Search grounding, and structured comparisons to turn election data into actionable voter education.

## Hackathon Journey: Idea, Planning, and AI Implementation

### The Initial Idea
**CivikSutra (The Civic Formula)** was conceived to solve a critical problem: bridging the information gap for Indian voters. The idea is to create a mobile-first, AI-powered election process education assistant that meets voters where they are. From finding the exact polling booth using GPS to researching candidates via Gemini AI with Google Search grounding, the app turns complex election data into actionable, easy-to-understand voter education.

### Planning the Approach
Taking an "Architect First, AI Executes" approach, we planned a highly scalable and productizable architecture before writing any code:
1. **Architecture Design:** A serverless monolith (Firebase Hosting for React PWA, Cloud Functions for Python backend, Firestore for caching).
2. **Delivery Phases:** Broken down into Foundation (Booth Finder), Intelligence (Candidate Research), Depth (Manifesto & Chat), and Polish (Multilingual).
3. **Security & Scale:** Ensured zero plaintext secrets, strict CORS, and Firebase Auth for secure, frictionless access.

### Module-Wise Implementation using AI
We leveraged AI extensively through intent-driven prompting and iterative refinement to build our modules:
- **Project Scaffolding:** Used AI to generate the initial folder structure, Dockerfiles, and deployment configurations.
- **Booth Finder Module:** Prompted AI to integrate the Google Maps JavaScript API with React, handling GPS coordinates and traffic-aware routing.
- **Candidate Intelligence:** Utilized Gemini 2.0 Flash for structured data extraction and comparison, summarizing candidate affidavits and party manifestos.
- **Assistant Chat:** Built a conversational election guide where AI helped implement the streaming responses and grounding with real-time Google Search results.
- **Multilingual Support:** Guided AI to build a seamless translation layer, making the app accessible in Hindi, English, and regional languages.

## Features

| Module | Description | Status |
|--------|-------------|--------|
| [Booth Finder](docs/feature-booth-finder.md) | GPS-based polling booth discovery, map navigation, traffic-aware timing, and ECI verification handoff | `deployed` |
| [Candidate Intelligence](docs/feature-candidate-intelligence.md) | Background search, comparative analysis, criminal/asset/education data | `implemented` |
| [Manifesto Comparison](docs/feature-manifesto-comparison.md) | Side-by-side party manifesto analysis and promise tracking | `implemented` |
| [Assistant Chat](docs/feature-assistant-chat.md) | Gemini-powered conversational election guide with grounding | `implemented` |
| [Voter Readiness](docs/feature-voter-readiness.md) | Eligibility check, election card application guide, voting day checklist | `implemented` |
| [Multilingual](docs/feature-multilingual.md) | Hindi, English, and regional language support via Gemini translation | `implemented` |

## Architecture

The app is a **React SPA** talking to a **Python FastAPI** backend over HTTPS. You can run it in either of these **equivalent** topologies (same `frontend/` and `functions/` code):

| Path | Static app | API | Typical use |
|------|------------|-----|-------------|
| **A — Firebase** | Firebase Hosting (CDN) | Cloud Functions (HTTP) wrapping the FastAPI app | Quick deploy, `firebase deploy`, public demo on `*.web.app` |
| **B — Cloud Run** | Container: `civiksutra-web` (nginx + built SPA) | Container: `civiksutra-api` (FastAPI) | [cloudbuild.yaml](cloudbuild.yaml) → Artifact Registry → Cloud Run |

Shared: **Firestore** (cache), **Gemini**, **Vertex** (FAQ embeddings), **Cloud Translation**, **Maps Platform**, etc. Full detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```
┌──────────────────────────────────────────────────────────────────┐
│  Browser (no EPIC / PII sent except what user types in forms)     │
└───────────────────────────────┬──────────────────────────────────┘
                                │ HTTPS
        ┌───────────────────────┴───────────────────────┐
        │  Static bundle: Firebase Hosting OR Cloud Run │
        │  `civiksutra-web` (React 18 + Vite)              │
        └───────────────────────┬───────────────────────┘
                                │ JSON / SSE
        ┌───────────────────────┴───────────────────────┐
        │  API: Cloud Functions HTTP OR Cloud Run          │
        │  `civiksutra-api` — booth / candidate / assistant│
        │  GeoService │ CandidateService │ ChatService …     │
        └───────────────────────┬───────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │  Firestore │ Gemini │ Vertex FAQ │ Translate│
        │  Maps (server) │ MyNeta / ECI scraping       │
        └─────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + Vite + Tailwind CSS | Mobile-first PWA, fast HMR, utility-first styling |
| Maps | Google Maps JavaScript API | Best India coverage, traffic layer, directions |
| Backend | FastAPI in Cloud Functions or Cloud Run (Python 3.12) | Same codebase; pick Firebase or containerized Cloud Run |
| AI | Gemini 2.0 Flash (Vertex AI) | Grounding with Google Search, streaming, multimodal |
| Database | Cloud Firestore | Real-time sync, offline support, TTL for cache |
| Auth | Firebase Auth (anonymous) | Zero-friction for civic app, no signup wall |
| Hosting | Firebase Hosting | CDN, custom domain, SPA routing, preview channels |
| Bot Protection | reCAPTCHA v3 | Already configured, score-based abuse prevention |

## Project Structure

```
election/
├── README.md
├── docs/
│   ├── PLAN.md                         # Delivery plan with tracking
│   ├── ARCHITECTURE.md                 # System design and data flow
│   ├── feature-booth-finder.md         # Module: booth discovery + navigation
│   ├── feature-candidate-intelligence.md # Module: candidate research + compare
│   ├── feature-manifesto-comparison.md # Module: manifesto analysis
│   ├── feature-assistant-chat.md       # Module: AI election guide
│   ├── feature-voter-readiness.md      # Module: voter preparation
│   └── feature-multilingual.md         # Module: language support
├── frontend/                           # React + Vite app
│   ├── src/
│   │   ├── components/
│   │   │   ├── booth/                  # Booth finder UI
│   │   │   ├── candidate/             # Candidate compare UI
│   │   │   ├── chat/                  # Chat interface
│   │   │   ├── voter/                 # Voter readiness UI
│   │   │   └── ui/                    # Shared primitives
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── lib/                       # API client, Firebase init
│   │   ├── types/                     # TypeScript interfaces
│   │   └── i18n/                      # Translation files
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── functions/                          # Firebase Cloud Functions
│   ├── src/
│   │   ├── api/                       # HTTP function handlers
│   │   │   ├── booth.py
│   │   │   ├── candidate.py
│   │   │   └── assistant.py
│   │   ├── services/                  # Business logic
│   │   │   ├── geo_service.py
│   │   │   ├── candidate_service.py
│   │   │   ├── chat_service.py
│   │   │   └── scraper_service.py
│   │   ├── models/                    # Pydantic schemas
│   │   └── core/                      # Config, auth, rate limiting
│   ├── tests/                         # Unit tests per module
│   │   ├── test_geo_service.py
│   │   ├── test_candidate_service.py
│   │   ├── test_chat_service.py
│   │   └── test_scraper_service.py
│   ├── requirements.txt
│   └── pyproject.toml
├── firebase.json
├── firestore.rules
├── firestore.indexes.json
├── .firebaserc
├── .env                               # Local dev (gitignored)
├── .env.example                       # Template (committed)
└── .gitignore
```

## Quick Start

```bash
# Prerequisites: Node.js 20+, Python 3.12+, Firebase CLI

# Clone and install
git clone <repo-url>
cd election

# Frontend
cd frontend && npm install

# Functions
cd ../functions && pip install -r requirements.txt

# Configure
cp .env.example .env
# Fill in your API keys

# Run locally
firebase emulators:start    # Functions + Firestore
cd frontend && npm run dev  # Vite dev server at :5173
```

## Quality & CI (Nirvachan-style gate)

- **Frontend:** from `frontend/` run `npm run validate` (TypeScript, ESLint, Vitest with coverage), `npm run test:e2e` (Playwright: Chromium + mobile; `@axe-core/playwright` on landing), and `npm run build` + `npm run lhci` (Lighthouse CI against production preview; see `frontend/lighthouserc.json`).
- **Cloud Functions:** from `functions/` run `pip install -e ".[test]"` then `python -m pytest tests/ -q --cov=src` (coverage fail-under 75% via `[tool.coverage.report]` in `pyproject.toml`).
- **CI:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on push/PR: frontend validate (includes **Prettier** `format:check`) + E2E, backend tests + coverage, Lighthouse CI.
- **CD (Firebase):** [`.github/workflows/deploy-firebase.yml`](.github/workflows/deploy-firebase.yml) runs on every push to `main` and deploys Hosting + Cloud Functions + Firestore. Configure **Actions → Secrets and variables** (Repository or `production` environment):
  - **Secrets:** `FIREBASE_TOKEN` (from `firebase login:ci`), `EP_GEMINI_API_KEY`, `EP_GOOGLE_MAPS_API_KEY`, `EP_RECAPTCHA_SECRET_KEY`
  - **Variables (optional):** `EP_GCP_PROJECT_ID`, `EP_CORS_ORIGINS` (JSON array string, e.g. `["https://YOUR.web.app"]`)
  - CI ([`ci.yml`](.github/workflows/ci.yml)) injects the same secrets/vars into jobs so builds and tests can use them; fork PRs do not receive secrets (env stays empty; tests use mocks).
- **Manual (before recording a demo):** keyboard-only pass on the journey tabs, chat send, and trust-banner links; Lighthouse in CI is not a substitute for focus order on custom controls.
- **Optional load check:** [docs/load-testing.md](docs/load-testing.md) and [`scripts/k6-health-smoke.js`](scripts/k6-health-smoke.js) for `/health` against Cloud Run after deploy.
- **CD (Cloud Build):** [`cloudbuild.yaml`](cloudbuild.yaml) builds the multi-stage SPA image (`Dockerfile`) and the FastAPI image (`Dockerfile.api`), pushes both to Artifact Registry, then deploys them to Cloud Run. Substitutions allow targeting different envs:
  ```bash
  gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=asia-south1,_AR_REPO=civiksutra,_FRONT_SERVICE=civiksutra-web,_API_SERVICE=civiksutra-api,_DEPLOY=true
  ```
  Set `_DEPLOY=false` for build-only validation runs (PR previews).

## Live Demo

Deployed Firebase app: **https://civiksutra-2604261729.web.app** (set your public URL if different in your fork).

**Demo video:** *Record a 2–3 minute walkthrough (see storyboard in [docs/PROMPT_JOURNEY.md](docs/PROMPT_JOURNEY.md)) and paste your Loom or YouTube URL here.*

**AI / prompt log:** [docs/PROMPT_JOURNEY.md](docs/PROMPT_JOURNEY.md)

**Data flow (PII / trust boundary):** [docs/DATA_FLOW.md](docs/DATA_FLOW.md)

**Security:** [SECURITY.md](SECURITY.md)

Current implemented slice:
- Booth Finder UI with GPS and manual search entry points.
- Nearby polling-place results with map rendering and fallback map preview.
- Walking/driving time, traffic level, and suggested best visit window.
- ECI verification handoff for official assigned booth lookup.
- Privacy stance: no voter-roll or EPIC details are stored by CivikSutra.

Important civic accuracy note: nearby polling places are not guaranteed to be the
voter's official assigned booth. The app routes users to ECI Electoral Search for
authoritative verification.

## Delivery Plan

See [docs/PLAN.md](docs/PLAN.md) for the full phased delivery plan with feature-level tracking.

| Phase | Scope | Target |
|-------|-------|--------|
| 1 - Foundation | Project scaffold, Firebase setup, GPS booth finder | Week 1 |
| 2 - Intelligence | Candidate search, grounding, comparative analysis | Week 2 |
| 3 - Depth | Manifesto comparison, assistant chat, voter readiness | Week 3 |
| 4 - Polish | Multilingual, PWA, deploy, testing | Week 4 |

## Data Sources

| Source | Purpose | Method |
|--------|---------|--------|
| Google Maps Platform | Booth location, traffic, directions | Maps JavaScript API + Directions API |
| Election Commission (ECI) | Booth lists, voter roll verification | NVSP portal integration |
| MyNeta.info / ADR | Candidate criminal records, assets, education | Structured data extraction |
| Google Search (Grounding) | Real-time candidate news, public record | Gemini grounding API |
| Party Websites | Manifestos, policy positions | Gemini summarization |

## License

MIT
