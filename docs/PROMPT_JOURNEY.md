# CivikSutra — AI-Assisted Prompt Journey

> This document records every significant AI-assisted development step, the
> prompts that drove them, the mistakes the model made, the architecture
> decisions we kept, and the metrics that prove the system works. It is the
> primary **Innovation** and **Presentation** evidence for the Hack2Skill
> Promptwards hackathon submission.

---

## 1. Development Philosophy

| Principle | Why |
|---|---|
| **Architect first, AI executes** | Agree on API shape, trust boundaries, and deploy path before writing a single line. AI generates faster than humans review, so the bottleneck is always the *spec*, not the *code*. |
| **Iterative narrowing** | When the model gets it wrong, don't re-prompt the entire task. Narrow the spec to the *exact failing assertion* (locator, env var, coverage floor) and re-run. |
| **Verification before claiming done** | Every milestone ends with `npm run validate`, `npm run test:e2e`, and `pytest tests/ --cov=src`. Green CI is the only "done" signal. |
| **Intent-driven prompts** | State the *what* and *why*, not the *how*. Let the AI propose implementation; correct if wrong. |

---

## 2. Verbatim Prompt Excerpts

Below are representative (lightly paraphrased) prompts from the actual session, in chronological order.

### 2.1 Scaffold

> "Create a Vite + React + TypeScript app with i18n (en/hi), a tabbed layout
> for booth finder, candidates, manifesto compare, voter guide, and chat, and a
> typed `lib/api` layer that targets a Python FastAPI backend."

**Outcome:** Generated the full `frontend/` directory with Vite config, React
Router, `i18n/` locale files, and typed fetch wrappers in `lib/chat-api.ts`.
Required one correction: the initial i18n setup used `react-intl` instead of
`react-i18next` — we re-prompted specifying `react-i18next` with
`LanguageDetector`.

### 2.2 Booth API

> "Implement `POST /booth/nearby` with Pydantic models, mock Google Maps /
> Places in pytest, and document that nearby results are hints — ECI Electoral
> Search is authoritative for the assigned booth."

**Outcome:** `geo_service.py` with `NearbyRequest`, `NearbyResponse`, distance
calculations, and a trust banner directing users to
`electoralsearch.eci.gov.in`. The initial mock missed the `directions` endpoint
— added in a follow-up prompt.

### 2.3 Gemini Function Calling

> "Wire Gemini function calling with tools for eligibility check, Vertex AI FAQ
> search, polling-location lookup, election timeline, and candidate search.
> Return `citations` and `tool_calls` in the JSON response for the React UI to
> display badges."

**Outcome:** `chat_service.py` refactored from string-matching intent detection
to native Gemini `function_declarations`. Five tools registered:
`check_eligibility`, `search_faq`, `find_polling_location`,
`get_election_timeline`, `search_candidates`. Each tool returns structured data
that the system prompt instructs Gemini to cite in its response.

### 2.4 Vertex AI Semantic FAQ Search

> "Create a VertexFAQService that embeds the faq_corpus at startup using
> text-embedding-004, caches the vectors, and on each query embeds the question
> and returns the top-3 entries by cosine similarity. Graceful fallback:
> keyword search if Vertex is unconfigured."

**Outcome:** `vertex_service.py` with `embed_corpus()` at init, `search()`
with cosine similarity, and `_keyword_fallback()` for environments without
Vertex credentials. Added 49 FAQ entries (now 55) to `faq_corpus.py`.

### 2.5 Security Middleware

> "Add security headers middleware for FastAPI: CSP, X-Frame-Options,
> X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP, CORP, HSTS.
> Also add a sliding-window per-IP rate limiter on /assistant/chat,
> /candidate/search, and /booth/nearby."

**Outcome:** `SecurityHeadersMiddleware` and `RateLimitMiddleware` in
`middleware/security.py`. Rate limiter uses an `asyncio.Lock` and
`collections.deque` per IP. Tests cover header injection, rate limiting at
boundary, and IP extraction.

### 2.6 Rate Limiting & Input Sanitisation

> "Add server-side input sanitisation for all user-facing text fields before
> they reach Gemini. Strip HTML tags, limit length, reject control characters.
> Never log raw user input."

**Outcome:** `input_sanitiser.py` with `sanitise_chat_message()` — strips HTML,
normalises whitespace, truncates at 2000 chars, rejects ASCII control codes.
Applied at the API layer before any service call.

### 2.7 Seven-Stage Voter Journey

> "Redesign the frontend navigation into a seven-stage guided civic flow:
> Eligibility → Register → Research → Compare → Locate → Vote → Ask AI Coach.
> Each stage maps to an existing component. Add i18n keys for all stages."

**Outcome:** `ElectionJourney.tsx` rewritten with `JOURNEY_STAGES` constant,
`StageMeta` type, `isActive`/`isCompleted` visual states, `aria-current="step"`.
`App.tsx` updated with `NAV_ENTRIES` and `VOTER_TAB_BY_STAGE` for deep-linking.
i18n files updated for all 7 stages in both `en` and `hi`.

### 2.8 Cloud Translation Service

> "Create a TranslationService wrapping Cloud Translation v3 with LRU cache,
> support for en/hi initially, and graceful fallback to source text if the API is
> unavailable. Expose it via POST /assistant/translate."

**Outcome:** `translation_service.py` with bounded `_TRANSLATION_CACHE` dict,
`MAX_INPUT_CHARS` clamping, lazy client init, and the `/assistant/translate`
endpoint. Expanded to 8 languages (en, hi, ta, te, bn, mr, gu, kn) in Phase 2.

### 2.9 Cloud Build CI/CD Pipeline

> "Create a cloudbuild.yaml with parallel backend/frontend test steps, Docker
> image builds for both frontend (Nginx) and API (FastAPI), push to Artifact
> Registry, and conditional Cloud Run deploy."

**Outcome:** Multi-step `cloudbuild.yaml` with substitutions for
`_PROJECT_ID`, `_REGION`, `_IMAGE_TAG`. Frontend Dockerfile uses multi-stage
build (Node for build → Nginx:alpine for serve). API Dockerfile uses
`python:3.12-slim` with non-root user `civiksutra`.

### 2.10 Playwright E2E + Accessibility

> "Add Playwright E2E specs: smoke tests for all 7 journey stages, an
> accessibility suite using axe-core with WCAG 2.1 AA tags, and a chat journey
> test that sends a message and verifies the response appears."

**Outcome:** `smoke.spec.ts`, `accessibility.spec.ts`, `chat-journey.spec.ts`.
Used `@axe-core/playwright` for automated accessibility audits. Added Desktop
Chrome and Mobile Safari projects.

---

## 3. When the Model Was Wrong

### 3.1 Playwright Locator Ambiguity

**Problem:** Smoke tests failed on `getByRole('button', { name: 'Ask AI' })`
because the new election journey row added a second "Ask AI" control. Strict
mode matched two nodes and threw.

**Root cause:** The model generated a flat locator without scoping to a
container.

**Fix:** Scoped assertions to `getByRole('navigation', { name: 'Main navigation' })`
for the tab bar and gave the journey strip `role="region"` with its own label.
This preserved coverage and matched how assistive tech exposes the UI.

```diff
- await page.getByRole('button', { name: 'Ask AI' }).click();
+ const nav = page.getByRole('navigation', { name: 'Main navigation' });
+ await nav.getByRole('button', { name: 'Ask AI' }).click();
```

### 3.2 Ruff D103 Docstring False Positives on Test Files

**Problem:** `ruff check` flagged every test function with `D103 Missing
docstring in public function`. Test functions are public by convention
(`test_xxx`) but documenting each one adds noise, not value.

**Root cause:** The model applied blanket `D` rules without per-file overrides.

**Fix:** Added `per-file-ignores` to `pyproject.toml`:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D101", "D102", "D103", "D106"]
```

### 3.3 Hindi String E501 False Positives

**Problem:** `ruff check` reported `E501 Line too long` on Hindi strings in
`QUICK_QUESTIONS` and `_generic_fallback` dicts. These are legitimate
multi-word Hindi sentences that cannot be meaningfully broken at 88 chars.

**Root cause:** The model tried to split the strings at word boundaries, but
Devanagari words are wider in char count and the splits broke readability.

**Fix:** Added `# noqa: E501` to the specific lines. Documented why in a code
comment referencing the Unicode string width issue.

---

## 4. Architecture Decisions Log

### 4.1 FastAPI Backend vs SPA-Only

NirvachanAI (our benchmark) uses a pure SPA with client-side API keys. We chose
a Python FastAPI backend because:

- **Security:** API keys (Gemini, Maps, Vertex, Translate) stay server-side.
  The SPA never sees credentials.
- **Function calling:** Gemini function calling requires server-side tool
  dispatch. Client-side tool execution would expose tool implementations.
- **Rate limiting:** Server-side sliding window is enforceable; client-side
  debounce is bypassable.
- **Testability:** Backend logic has 119 unit tests at 76%+ coverage. SPA-only
  architectures push all logic into untestable API calls.

### 4.2 Function Calling over String-Matching Intent

The first version of `chat_service.py` used regex-based intent detection
(`if "eligib" in message.lower()`). This was fragile and missed Hindi queries.
Native Gemini function calling:

- Handles multilingual queries without keyword lists.
- Returns structured JSON that the UI can display as tool-call badges.
- Scales to new tools without adding more regex branches.

### 4.3 LRU Cache on Translation Service

Cloud Translation v3 charges per character. The LRU cache (bounded at 1024
entries by default, configurable via `EP_TRANSLATE_CACHE_SIZE`) ensures:

- Repeated queries (e.g., the same FAQ answer shown to multiple users) cost
  one API call, not N.
- Cache eviction is oldest-first via dict insertion order (Python 3.7+).
- The cache is per-process, so each Cloud Function cold start gets a fresh
  cache — no stale data persists across deploys.

### 4.4 Server-Side Rate Limiting vs Client Debounce

Client-side debounce is a UX improvement, not a security measure. Anyone with
`curl` can bypass it. The server-side `RateLimitMiddleware` uses a
sliding-window counter per IP address, implemented with `asyncio.Lock` for
thread safety in the async FastAPI event loop. The 30-request/60-second window
balances responsiveness with abuse prevention.

### 4.5 Firebase Functions Entry Point as Manual Router

Firebase Cloud Functions (Python) does not use ASGI routing. The `main.py`
entry point is a single `@https_fn.on_request` function that manually dispatches
on `req.method` and `req.path`. This pattern:

- Keeps the Firebase SDK happy (single export per function).
- Allows parallel development of FastAPI routes in `src/api/` that are testable
  with `httpx.AsyncClient`.
- Requires syncing `main.py` whenever a new route is added — a known
  maintenance cost we accept for deploy simplicity.

---

## 5. Metrics

| Metric | Value |
|---|---|
| Backend tests | 119 |
| Backend coverage | 76.32% (target: 85%+) |
| Frontend unit tests (Vitest) | 6 |
| Playwright E2E specs | 3 (smoke, accessibility, chat journey) |
| Python source files | 25 |
| Frontend source files (TS/TSX) | 37 |
| FAQ corpus entries | 55 |
| Supported languages | 8 (en, hi, ta, te, bn, mr, gu, kn) |
| GCP services integrated | 7+ (Gemini, Vertex AI, Maps, Translate, Cloud NL, Firestore, Cloud Run) |
| Docker images | 2 (frontend Nginx, API FastAPI) |
| CI/CD pipeline steps | 6 (lint, test, build x2, push, deploy) |

---

## 6. Build Decisions (from early development)

1. **One Firebase deployment** — Hosting, Python Cloud Functions, and Firestore
   rules ship together with `firebase deploy`. Frontend and function code live
   in separate directories as source boundaries, not separate deployments.

2. **Booth Finder first** — Implemented the highest-impact voter journey step
   before candidates or manifesto. Built GPS/manual search, nearby booth cards,
   directions, traffic level, and best visit window.

3. **Responsible civic accuracy** — Separated "nearby polling place" from
   "official assigned booth." Added ECI Electoral Search handoff. Never store
   EPIC or voter personal data.

4. **Verification loop** — Backend: `python -m pytest tests -q`. Frontend:
   `npm test`. Build: `npm run build`. Live smoke tests against Firebase.

---

## 7. Live Demo

**URL:** https://civiksutra-2604261729.web.app

**GitHub:** https://github.com/gsaraiya/election

---

## 8. Demo Video Storyboard (2-3 min)

| Timestamp | Scene | Content |
|---|---|---|
| 0:00–0:20 | Problem statement | 950M voters, complex multi-type election system, information gap for first-time voters |
| 0:20–0:50 | Journey walkthrough | Click through all 7 stages: Eligibility → Register → Research → Compare → Locate → Vote → Ask AI |
| 0:50–1:30 | AI coach demo | Ask a question, show tool-call badges firing (eligibility check, FAQ lookup), show citations |
| 1:30–1:50 | Language toggle | Switch to Hindi, show dynamically translated AI response via Cloud Translation |
| 1:50–2:20 | Technical depth | GitHub CI passing, Lighthouse scores, coverage report |
| 2:20–2:40 | Architecture | `cloudbuild.yaml`, Terraform config, dual Docker images |
| 2:40–3:00 | Close | Non-partisan stance, ECI/NVSP links, trust banner |

---

## 9. Trust Boundary Diagram

See [DATA_FLOW.md](DATA_FLOW.md) for a Mermaid diagram suitable for slides or
README copy-paste. The key invariant: **no API key, GCP credential, or voter
PII ever reaches the browser.** All sensitive operations happen server-side
behind the Firebase Functions proxy.
