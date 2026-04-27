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

Single monolithic deployment on Firebase. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details.

```
┌─────────────────────────────────────────────────────┐
│              Firebase Hosting (PWA)                  │
│         React 18 + Vite + Tailwind CSS              │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ │
│  │  Map    │ │  Chat   │ │ Compare  │ │ Voter   │ │
│  │  View   │ │  UI     │ │ Tables   │ │ Guide   │ │
│  └────┬────┘ └────┬────┘ └────┬─────┘ └────┬────┘ │
│       └───────────┴───────────┴─────────────┘      │
│                       │                             │
└───────────────────────┼─────────────────────────────┘
                        │ HTTPS
┌───────────────────────┼─────────────────────────────┐
│          Firebase Cloud Functions (Python)           │
│                                                     │
│  ┌────────────┐ ┌─────────────┐ ┌────────────────┐ │
│  │ Booth API  │ │ Candidate   │ │ Assistant API  │ │
│  │ geo/traffic│ │ API search  │ │ Gemini stream  │ │
│  └─────┬──────┘ └──────┬──────┘ └───────┬────────┘ │
│        │               │                │           │
│  ┌─────┴───────────────┴────────────────┴─────────┐ │
│  │            Service Layer                       │ │
│  │  GeoService │ CandidateService │ ChatService   │ │
│  └────────────────────────────────────────────────┘ │
│                        │                            │
│  ┌─────────────────────┴──────────────────────────┐ │
│  │         External Integrations                  │ │
│  │  Google Maps Platform  │  Gemini API           │ │
│  │  ECI / MyNeta data     │  Firestore (cache)    │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + Vite + Tailwind CSS | Mobile-first PWA, fast HMR, utility-first styling |
| Maps | Google Maps JavaScript API | Best India coverage, traffic layer, directions |
| Backend | Firebase Cloud Functions (Python 3.12) | Single deploy target, auto-scaling, no infra management |
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

## Live Demo

Deployed Firebase app: https://civiksutra-2604261729.web.app

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
