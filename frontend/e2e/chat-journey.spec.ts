import { expect, test } from "@playwright/test";

import { stubAssistantTimeline } from "./stub-assistant-timeline";

test.describe("AI coach journey", () => {
  test("displays quick questions and surfaces tool-call badges", async ({ page }) => {
    await stubAssistantTimeline(page);
    await page.route("**/assistant/questions*", async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          questions: [
            "What documents do I need to vote?",
            "Find my polling booth",
            "How do EVMs work?",
          ],
        }),
      });
    });

    await page.route("**/assistant/chat", async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          response:
            "You are eligible to vote. Carry your EPIC card and a voter slip. Polling stations are open 7am-6pm.",
          session_id: "test-session",
          citations: [
            { source: "Election Commission of India", url: "https://eci.gov.in" },
          ],
          tokens_used: 32,
          tool_calls: [
            {
              tool_name: "check_voter_eligibility",
              args: { age: 21, citizenship: "indian" },
              result_summary: "eligible=True",
            },
            {
              tool_name: "lookup_election_faq",
              args: { query: "voting documents" },
              result_summary: "matches=1",
            },
          ],
        }),
      });
    });

    await page.goto("/");
    const nav = page.getByRole("navigation", { name: "Main navigation" });
    await nav.getByRole("button", { name: "Ask AI", exact: true }).click();

    await expect(
      page.getByRole("button", { name: "What documents do I need to vote?" })
    ).toBeVisible();

    const input = page.getByRole("textbox", { name: /chat message input/i });
    await input.fill("Am I eligible at 21 to vote?");
    await page.getByRole("button", { name: /send/i }).click();

    await expect(page.getByText("You are eligible to vote.")).toBeVisible();
    await expect(page.getByText("eligible=True")).toBeVisible();
    await expect(page.getByText("matches=1")).toBeVisible();
    await expect(
      page
        .locator(".chat-citations")
        .getByRole("link", { name: "Election Commission of India" })
    ).toHaveAttribute("href", "https://eci.gov.in");
  });

  test("graceful error surfaces when chat API fails", async ({ page }) => {
    await stubAssistantTimeline(page);
    await page.route("**/assistant/questions*", async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ questions: [] }),
      });
    });

    await page.route("**/assistant/chat", async (route) => {
      await route.fulfill({ status: 500, body: "boom" });
    });

    await page.goto("/");
    const nav = page.getByRole("navigation", { name: "Main navigation" });
    await nav.getByRole("button", { name: "Ask AI", exact: true }).click();

    const input = page.getByRole("textbox", { name: /chat message input/i });
    await input.fill("Test failure");
    await page.getByRole("button", { name: /send/i }).click();

    await expect(page.locator(".chat-msg--assistant").last()).toBeVisible();
    const lastAssistant = page.locator(".chat-msg--assistant").last();
    const errorText = await lastAssistant.innerText();
    expect(errorText.length).toBeGreaterThan(0);
  });
});
