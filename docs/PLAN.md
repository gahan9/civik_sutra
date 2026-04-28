# Delivery Plan

Feature-wise phased delivery with unit test tracking for each module.

## README alignment (important)

The [README](../README.md) describes **shipped, user-facing modules** (Booth Finder, candidates, manifesto, voter guide, chat, i18n, etc.). The checkbox tables in this file are **historical / granular engineering milestones**; not every cell is re-audited when a feature goes live. If a line still shows `[ ]` while the README marks the feature as implemented, **trust the README and source** for "does the app include this feature?" and use this plan for **deep delivery tracking** and test mapping.

## Phase Overview

```
Phase 1: Foundation        ──▶  Phase 2: Intelligence    ──▶  Phase 3: Depth           ──▶  Phase 4: Polish
├─ Project scaffold              ├─ Candidate search          ├─ Manifesto comparison       ├─ Multilingual (i18n)
├─ Firebase config               ├─ Grounding search          ├─ Assistant chat              ├─ PWA config
├─ Booth finder (GPS)            ├─ Comparative analysis      ├─ Voter readiness             ├─ reCAPTCHA
├─ Map navigation                ├─ Background check          └─ Voter checklist             ├─ Performance audit
├─ Traffic-based timing          └─ Tabular output                                           └─ Firebase deploy
└─ Booth verification
```

---

## Phase 1: Foundation

**Goal**: User can open the app, grant GPS, find nearby booths, get directions with traffic awareness.

### Deliverables

| # | Deliverable | Module | Test File | Status |
|---|------------|--------|-----------|--------|
| 1.1 | Firebase project init (`firebase.json`, `.firebaserc`, `firestore.rules`) | infra | manual verification | `[ ]` |
| 1.2 | Vite + React + Tailwind scaffold with PWA manifest | frontend | `npm run build` passes | `[ ]` |
| 1.3 | Firebase Cloud Functions scaffold (Python 3.12) | functions | `pytest functions/tests/` | `[ ]` |
| 1.4 | Core config module (`core/config.py`) with Pydantic Settings | functions | `test_config.py` | `[ ]` |
| 1.5 | GPS location hook (`useGeolocation`) | frontend | `hooks/__tests__/useGeolocation.test.ts` | `[x]` |
| 1.6 | Booth data model + Firestore schema | functions | `test_models.py` | `[ ]` |
| 1.7 | `GeoService.find_nearby_booths(lat, lng, radius)` | functions | `test_geo_service.py::test_find_nearby` | `[ ]` |
| 1.8 | `GeoService.get_directions(origin, destination)` | functions | `test_geo_service.py::test_directions` | `[ ]` |
| 1.9 | `GeoService.get_traffic_estimate(origin, destination)` | functions | `test_geo_service.py::test_traffic` | `[ ]` |
| 1.10 | `GeoService.suggest_best_visit_time(booth_id)` | functions | `test_geo_service.py::test_visit_time` | `[ ]` |
| 1.11 | Booth verification link to ECI/NVSP | functions | `test_geo_service.py::test_verify_booth` | `[ ]` |
| 1.12 | Map component with booth markers | frontend | `components/booth/__tests__/BoothMap.test.tsx` | `[x]` |
| 1.13 | Booth detail panel (address, timing, traffic) | frontend | `components/booth/__tests__/BoothDetail.test.tsx` | `[x]` |
| 1.14 | API route: `POST /booth/nearby` | functions | `test_booth_api.py::test_nearby_endpoint` | `[x]` |
| 1.15 | API route: `POST /booth/directions` | functions | `test_booth_api.py::test_directions_endpoint` | `[x]` |
| 1.16 | API route: `GET /booth/verify/{epic_number}` | functions | `test_booth_api.py::test_verify_endpoint` | `[x]` |

### Exit Criteria
- [ ] User grants GPS permission and sees nearby booths on a map
- [ ] Tapping a booth shows directions with estimated travel time
- [ ] Traffic-aware visit time suggestion is displayed
- [ ] EPIC verification redirects to NVSP with pre-filled data
- [ ] All unit tests pass: `pytest functions/tests/test_geo_service.py`

---

## Phase 2: Intelligence

**Goal**: User can search candidates by constituency, view rigorous background analysis, and compare candidates in a structured table.

### Deliverables

| # | Deliverable | Module | Test File | Status |
|---|------------|--------|-----------|--------|
| 2.1 | Candidate data model (Pydantic) | functions | `test_models.py::test_candidate_model` | `[ ]` |
| 2.2 | `ScraperService.fetch_myneta_candidates(constituency)` | functions | `test_scraper_service.py::test_myneta` | `[ ]` |
| 2.3 | `ScraperService.fetch_eci_affidavit(candidate_id)` | functions | `test_scraper_service.py::test_affidavit` | `[ ]` |
| 2.4 | `CandidateService.search_by_location(lat, lng)` | functions | `test_candidate_service.py::test_search_location` | `[ ]` |
| 2.5 | `CandidateService.search_by_constituency(name)` | functions | `test_candidate_service.py::test_search_constituency` | `[ ]` |
| 2.6 | `CandidateService.grounding_search(candidate_name)` | functions | `test_candidate_service.py::test_grounding` | `[ ]` |
| 2.7 | `CandidateService.background_check(candidate_id)` | functions | `test_candidate_service.py::test_background` | `[ ]` |
| 2.8 | `CandidateService.compare(candidate_ids: list)` | functions | `test_candidate_service.py::test_compare` | `[ ]` |
| 2.9 | Firestore caching layer for candidate data (TTL: 24h) | functions | `test_candidate_service.py::test_cache` | `[ ]` |
| 2.10 | Comparative analysis table builder (structured output) | functions | `test_candidate_service.py::test_table_builder` | `[ ]` |
| 2.11 | Candidate search UI with constituency input | frontend | `components/candidate/__tests__/SearchForm.test.tsx` | `[ ]` |
| 2.12 | Candidate card component (photo, party, key stats) | frontend | `components/candidate/__tests__/CandidateCard.test.tsx` | `[ ]` |
| 2.13 | Comparison table component (side-by-side) | frontend | `components/candidate/__tests__/CompareTable.test.tsx` | `[ ]` |
| 2.14 | API route: `POST /candidate/search` | functions | `test_candidate_api.py::test_search` | `[ ]` |
| 2.15 | API route: `GET /candidate/{id}/background` | functions | `test_candidate_api.py::test_background` | `[ ]` |
| 2.16 | API route: `POST /candidate/compare` | functions | `test_candidate_api.py::test_compare` | `[ ]` |

### Exit Criteria
- [ ] User enters constituency or GPS auto-detects it
- [ ] Candidate list loads with key stats (party, education, criminal cases, assets)
- [ ] Grounding search returns recent news and public record for any candidate
- [ ] Side-by-side comparison table renders for 2-4 selected candidates
- [ ] Comparison includes: education, criminal cases, assets, past work, future probability
- [ ] All unit tests pass: `pytest functions/tests/test_candidate_service.py`

---

## Phase 3: Depth

**Goal**: Manifesto comparison, conversational AI assistant, and voter preparation checklist.

### Deliverables

| # | Deliverable | Module | Test File | Status |
|---|------------|--------|-----------|--------|
| 3.1 | `CandidateService.fetch_manifesto(party_name)` | functions | `test_candidate_service.py::test_manifesto_fetch` | `[ ]` |
| 3.2 | `CandidateService.compare_manifestos(party_names)` | functions | `test_candidate_service.py::test_manifesto_compare` | `[ ]` |
| 3.3 | Manifesto category extraction (economy, health, education, etc.) | functions | `test_candidate_service.py::test_manifesto_categories` | `[ ]` |
| 3.4 | Manifesto comparison UI (category-wise side-by-side) | frontend | `components/candidate/__tests__/ManifestoCompare.test.tsx` | `[ ]` |
| 3.5 | `ChatService` with Gemini streaming + system prompt | functions | `test_chat_service.py::test_stream` | `[ ]` |
| 3.6 | `ChatService.with_grounding()` for search-backed answers | functions | `test_chat_service.py::test_grounding` | `[ ]` |
| 3.7 | `ChatService` tool integration (booth finder, candidate search) | functions | `test_chat_service.py::test_tools` | `[ ]` |
| 3.8 | Chat conversation memory (Firestore session) | functions | `test_chat_service.py::test_memory` | `[ ]` |
| 3.9 | Chat UI with streaming response | frontend | `components/chat/__tests__/ChatWindow.test.tsx` | `[ ]` |
| 3.10 | Suggested questions / quick actions in chat | frontend | `components/chat/__tests__/QuickActions.test.tsx` | `[ ]` |
| 3.11 | Voter eligibility checker (interactive questionnaire) | frontend | `components/voter/__tests__/EligibilityCheck.test.tsx` | `[ ]` |
| 3.12 | Election card application guide (NVSP walkthrough) | frontend | `components/voter/__tests__/CardApplication.test.tsx` | `[ ]` |
| 3.13 | Voting day checklist (documents, dos/don'ts) | frontend | `components/voter/__tests__/Checklist.test.tsx` | `[ ]` |
| 3.14 | API route: `POST /assistant/chat` (streaming) | functions | `test_assistant_api.py::test_chat_stream` | `[ ]` |
| 3.15 | API route: `POST /manifesto/compare` | functions | `test_candidate_api.py::test_manifesto_compare` | `[ ]` |
| 3.16 | Rate limiting middleware (per `.env` config) | functions | `test_middleware.py::test_rate_limit` | `[ ]` |

### Exit Criteria
- [ ] Manifesto comparison renders category-wise table for 2+ parties
- [ ] Chat streams responses with grounding citations
- [ ] Chat can invoke booth finder and candidate search as tools
- [ ] Voter eligibility questionnaire gives clear pass/fail with next steps
- [ ] NVSP application guide is step-by-step with external links
- [ ] All unit tests pass for Phase 3 modules

---

## Phase 4: Polish

**Goal**: Multilingual support, PWA offline, reCAPTCHA, performance, and Firebase deploy.

### Deliverables

| # | Deliverable | Module | Test File | Status |
|---|------------|--------|-----------|--------|
| 4.1 | i18n framework setup (`react-i18next`) | frontend | `i18n/__tests__/i18n.test.ts` | `[ ]` |
| 4.2 | Hindi translation file | frontend | manual review | `[ ]` |
| 4.3 | Gemini-powered dynamic translation for AI responses | functions | `test_chat_service.py::test_translation` | `[ ]` |
| 4.4 | Language selector component | frontend | `components/ui/__tests__/LanguageSelector.test.tsx` | `[ ]` |
| 4.5 | PWA service worker (offline checklist, cached booth data) | frontend | Lighthouse PWA audit | `[ ]` |
| 4.6 | reCAPTCHA v3 integration (frontend token + backend verify) | both | `test_middleware.py::test_recaptcha` | `[ ]` |
| 4.7 | Error boundary and fallback UI | frontend | `components/ui/__tests__/ErrorBoundary.test.tsx` | `[ ]` |
| 4.8 | Loading skeletons for all data-fetching views | frontend | visual review | `[ ]` |
| 4.9 | Firebase Hosting deploy configuration | infra | `firebase deploy --only hosting` | `[ ]` |
| 4.10 | Cloud Functions deploy | infra | `firebase deploy --only functions` | `[ ]` |
| 4.11 | Firestore security rules finalized | infra | emulator test | `[ ]` |
| 4.12 | Lighthouse performance audit (target: 90+ mobile) | frontend | Lighthouse CI | `[ ]` |
| 4.13 | End-to-end smoke test | both | manual + Playwright | `[ ]` |

### Exit Criteria
- [ ] App works in Hindi and English with seamless switching
- [ ] PWA installable on mobile, offline checklist accessible
- [ ] reCAPTCHA blocks bot abuse without user friction
- [ ] Lighthouse mobile score >= 90 (performance, a11y, best practices)
- [ ] Deployed to Firebase and accessible via public URL

---

## Test Strategy

### Backend (Firebase Cloud Functions)

```
functions/tests/
├── test_config.py              # Config loading, env validation
├── test_models.py              # Pydantic model validation
├── test_geo_service.py         # Booth finder, directions, traffic
├── test_candidate_service.py   # Search, compare, background, manifesto
├── test_chat_service.py        # Gemini streaming, grounding, tools
├── test_scraper_service.py     # MyNeta, ECI data extraction
├── test_booth_api.py           # Booth HTTP endpoints
├── test_candidate_api.py       # Candidate HTTP endpoints
├── test_assistant_api.py       # Chat HTTP endpoints
├── test_middleware.py          # Rate limiting, reCAPTCHA, auth
└── conftest.py                 # Shared fixtures, mocks
```

**Run all**: `cd functions && pytest tests/ -v --tb=short`

**Coverage target**: 80%+ on service layer, 60%+ on API layer.

### Frontend

```
frontend/src/**/__tests__/
├── hooks/useGeolocation.test.ts
├── components/booth/*.test.tsx
├── components/candidate/*.test.tsx
├── components/chat/*.test.tsx
├── components/voter/*.test.tsx
└── components/ui/*.test.tsx
```

**Run all**: `cd frontend && npm test`

**Coverage target**: 70%+ on hooks and service functions.

### Mocking Strategy

| External Dependency | Mock Approach |
|---------------------|---------------|
| Google Maps API | Fixture JSON responses |
| Gemini API | `unittest.mock.AsyncMock` with canned responses |
| Firestore | Firebase emulator or `unittest.mock` |
| MyNeta/ECI scraping | Saved HTML fixtures in `tests/fixtures/` |
| GPS (frontend) | Mock `navigator.geolocation` |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google Maps API cost overrun | High | Client-side caching, debounced requests, daily quota in `.env` |
| MyNeta HTML structure changes | Medium | Defensive parsing, fallback to Gemini grounding |
| Gemini rate limits during demo | High | Response caching in Firestore, graceful fallback messages |
| GPS denied by user | Medium | Manual constituency/pincode input as fallback |
| Election data staleness | Medium | TTL-based cache invalidation (24h for candidates, 7d for manifesto) |
| Firebase cold start latency | Medium | Min instances = 1 for demo, connection pre-warming |
