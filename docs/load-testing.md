# Load testing (optional release checklist)

CivikSutra APIs are not designed for unbounded public abuse; use this **only** to sanity-check the **API** service after deploy (e.g. Cloud Run `civiksutra-api`).

## Health endpoint

The FastAPI app exposes `GET /health` (see [`functions/src/app.py`](../functions/src/app.py)). In production, replace `BASE` with your API URL.

## k6 (example)

Install [k6](https://k6.io/) and run against **staging** only — not production demos during judging.

Script: [`scripts/k6-health-smoke.js`](../scripts/k6-health-smoke.js).

```bash
export BASE=https://YOUR-API-URL.run.app
k6 run scripts/k6-health-smoke.js
```

Document **p95 latency** and **error rate** in your release notes if you use this in a **Technical depth** write-up. CI does **not** run k6 by default (flaky on shared runners).
