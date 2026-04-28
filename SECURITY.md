# Security

CivikSutra is a civic education and voter information assistant. This document describes how we handle credentials, transport, and reporting.

## Secrets and API keys

- **No secrets in source control.** Use `.env` (local, gitignored) and Firebase/Secret Manager in production. Start from [`.env.example`](.env.example) if present.
- **Restrict keys in Google Cloud Console.** For Maps, Gemini, and other APIs, use HTTP referrer or bundle ID restrictions, least-privilege service accounts, and separate keys for dev vs production where practical.
- **Do not log PII** (EPIC, phone, full address) in application logs. Structured logs should use event names and anonymised metadata only for analytics.

## Transport and hosting

- The production app is served over **HTTPS** (Firebase Hosting). Emulators and local Vite use HTTP for development only.
- The Python API in Cloud Functions enforces an **explicit CORS allowlist** in [`functions/src/app.py`](functions/src/app.py). Do not use `allow_origins=["*"]` in production.

## Client-side risk

- The frontend may load **Google Maps JavaScript API** and **Gemini**-backed features. Keys exposed to the client must be restricted; treat them as "public" but **bounded** by domain and API surface.
- **Google Calendar** deep-links in the UI open `calendar.google.com` with pre-filled, **illustrative** events. Users should replace dates with the official ECI / state schedule.

## Dependency hygiene

- Run `npm audit` / `pip-audit` in CI and patch critical issues before release.
- Prefer pinned or SemVer-locked dependencies in `package-lock.json` and `pyproject.toml` / lockfiles as adopted by the repo.

## Reporting vulnerabilities

- Open a private security advisory on GitHub, or contact the maintainers with a clear subject line (e.g. "CivikSutra security report").
- Do not open public issues for undisclosed high-severity bugs until a fix is coordinated.

## Disclaimer

- CivikSutra does not replace the **Election Commission of India** or state CEOs for official rolls, dates, or results. All electoral facts must be confirmed with official sources.
