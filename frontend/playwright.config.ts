import { defineConfig, devices } from "@playwright/test";

const host = "127.0.0.1";
const port = 5173;
const baseURL = `http://${host}:${port}`;

/**
 * E2E tests start the Vite dev server. Run from `frontend/`: `npm run test:e2e`.
 * CI: same — dev server avoids requiring a prebuilt `dist/`.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : 4,
  reporter: process.env.CI ? "github" : "list",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL,
    trace: "on-first-retry",
    navigationTimeout: 30_000,
    actionTimeout: 15_000,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 5"] } },
  ],
  webServer: {
    command: `npx vite --host ${host} --port ${String(port)}`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
