import type { Page } from "@playwright/test";

/** Avoid proxy 404/502 to a local API when E2E runs without the FastAPI server. */
export async function stubAssistantTimeline(page: Page): Promise<void> {
  await page.route("**/assistant/timeline**", async (route) => {
    await route.fulfill({
      status: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ events: [], count: 0 }),
    });
  });
}
