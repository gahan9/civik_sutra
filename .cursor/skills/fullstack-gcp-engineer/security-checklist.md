# Security Checklist

Pre-deployment verification for GCP full stack applications.

## Secrets & Credentials

- [ ] All secrets stored in Secret Manager -- zero in code, env files, or Docker images.
- [ ] `.env` files listed in `.gitignore` and `.dockerignore`.
- [ ] Service account keys: prefer Workload Identity Federation over downloaded JSON keys.
- [ ] API keys restricted by IP, referrer, or API in GCP Console.
- [ ] Firebase config (client-side) contains no server secrets -- it's public by design.

## Authentication & Authorization

- [ ] Firebase ID tokens verified server-side on every protected endpoint.
- [ ] Custom claims used for RBAC -- not client-side role checks alone.
- [ ] Token expiry handled: short-lived access tokens, server-managed refresh.
- [ ] Admin endpoints require elevated claims, not just authentication.
- [ ] OAuth scopes minimized to exact permissions needed.

## API Security

- [ ] CORS: explicit origin allowlist. No `*` in production.
- [ ] Rate limiting configured (Cloud Armor or application-level).
- [ ] Input validation via Pydantic -- reject unknown fields, enforce types and ranges.
- [ ] File uploads: type validation, size limits, virus scanning.
- [ ] SQL injection: parameterized queries only. ORM preferred over raw SQL.
- [ ] No stack traces or internal errors exposed in API responses.
- [ ] HTTPS enforced -- HTTP redirect or HSTS header.

## Infrastructure

- [ ] IAM: least privilege. Service accounts scoped per service, not shared.
- [ ] No `roles/owner` or `roles/editor` on service accounts.
- [ ] VPC Service Controls for sensitive data perimeters.
- [ ] Cloud Armor WAF rules enabled on public-facing load balancers.
- [ ] Audit logging enabled (Cloud Audit Logs) for admin and data access.
- [ ] Firestore security rules deployed and tested with emulator.

## Frontend

- [ ] CSP (Content Security Policy) headers configured.
- [ ] No secrets in client-side code or environment variables prefixed with `NEXT_PUBLIC_` / `VITE_`.
- [ ] XSS: React auto-escapes by default -- verify no `dangerouslySetInnerHTML` without sanitization.
- [ ] Dependencies audited: `npm audit` clean or exceptions documented.
- [ ] Source maps disabled in production builds.

## Data Protection

- [ ] PII encrypted at rest (Firestore/Cloud SQL default) and in transit (TLS).
- [ ] PII excluded from logs, error messages, and analytics.
- [ ] Data retention policies defined and enforced (Firestore TTL, GCS lifecycle).
- [ ] Backups configured for Cloud SQL. Firestore has automatic backups.
- [ ] BigQuery: column-level security or authorized views for sensitive data.

## CI/CD Pipeline

- [ ] `pip-audit` (Python) and `npm audit` (Node) in CI -- fail on critical/high.
- [ ] Container image scanning via Artifact Registry vulnerability scanning.
- [ ] No `--no-verify` flags in deployment scripts.
- [ ] Production deploys require approval gate (Cloud Build or GitHub Actions).
- [ ] Rollback strategy documented and tested.

## AI/ML Specific

- [ ] Prompt injection mitigations: input sanitization, output validation.
- [ ] AI responses validated before persisting or displaying (no blind trust).
- [ ] Token/cost budgets enforced per user and per request.
- [ ] PII stripped before sending to external AI APIs.
- [ ] Model outputs logged for audit (without PII).
- [ ] Safety settings explicitly configured on Gemini/Vertex AI calls.

## Monitoring & Incident Response

- [ ] Error Reporting enabled in GCP.
- [ ] Uptime checks configured for critical endpoints.
- [ ] Alerting policies for error rate spikes, latency, and cost anomalies.
- [ ] Incident response runbook documented.
- [ ] Log-based metrics for security events (auth failures, rate limit hits).
