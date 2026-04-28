# AI-assisted build log (Promptwards / submission)

This documents **how** CivikSutra was built with AI assistance — for **Innovation** and **Presentation** scoring.

## Principles

- **Architect first, AI executes:** agree on API shape, trust boundaries, and deploy path (Firebase vs Cloud Run) before coding.
- **Iterative fix:** when generated code was wrong, we narrowed the spec (locators, env names, coverage floors) and re-ran.
- **Verification:** `npm run validate`, `npm run test:e2e`, and `pytest tests/ --cov=src` before claiming a milestone done.

## Prompt sequence used during development (representative)

These are paraphrased from the actual session; wording may differ slightly.

1. **Scaffold** — *"Create a Vite + React + TypeScript app with i18n (en/hi), a tabbed layout for booth finder, candidates, manifesto compare, voter guide, and chat, and a typed `lib/api` layer that targets a Python FastAPI backend."*

2. **Booth API** — *"Implement `POST /booth/nearby` with Pydantic models, mock Google Maps / Places in pytest, and document that nearby results are hints — ECI Electoral Search is authoritative for the assigned booth."*

3. **Chat + tools** — *"Wire Gemini function calling with tools for eligibility, Vertex FAQ search, polling location, election timeline, and candidate search; return `citations` and `tool_calls` in the JSON response for the React UI."*

4. **Guardrails** — *"Extend the system prompt so the coach refuses voting recommendations, hedges state-specific dates, and never claims legal advice; add pytest that the prompt string still contains those rules."*

5. **CI / quality gate** — *"Add GitHub Actions: frontend `validate` (tsc, eslint, vitest+coverage), Playwright E2E with Chromium + mobile project, Lighthouse CI after build, and functions `pytest --cov=src` with fail-under 75%."*

6. **Trust UI** — *"Add a persistent trust banner with links to eci.gov.in, ECI Electoral Search, and NVSP; in chat, show a short note when an assistant message has no web citations and no tool calls."*

## When the model was wrong (and how we fixed it)

Early **Playwright** smoke tests failed on `getByRole('button', { name: 'Ask AI' })` because the new **election journey** row added a second "Ask AI" control. Strict mode then matched two nodes. We did **not** bulk-`skip` the test: we **scoped** assertions to `getByRole('navigation', { name: 'Main navigation' })` for the main tab bar and gave the journey strip `role="region"` with its own label. That preserved coverage and matched how assistive tech exposes the UI.

## Demo video

- **Target length:** 2–3 minutes.
- **Storyboard:** problem (access to accurate election process info) → seven-stage journey → booth or chat with **citations** → click ECI/NVSP from trust banner → 30s on AI + CI → close with non-partisan stance.
- **Link:** add your Loom or YouTube URL in the [README](../README.md) **Live Demo** section when recorded.

## Trust boundary diagram

See [DATA_FLOW.md](DATA_FLOW.md) for a Mermaid diagram suitable for slides or README copy-paste.
