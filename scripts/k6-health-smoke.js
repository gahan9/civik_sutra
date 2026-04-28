/**
 * Optional k6 smoke test for the FastAPI /health endpoint.
 * Usage: BASE=https://your-api.run.app k6 run scripts/k6-health-smoke.js
 */
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 5,
  duration: "30s",
  thresholds: { http_req_failed: ["rate<0.05"] },
};

export default function () {
  const base = __ENV.BASE || "http://127.0.0.1:8080";
  const res = http.get(`${base}/health`);
  check(res, { "status 200": (r) => r.status === 200 });
  sleep(0.2);
}
