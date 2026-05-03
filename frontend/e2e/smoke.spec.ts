import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { stubAssistantTimeline } from "./stub-assistant-timeline";

test.describe("CivikSutra smoke", () => {
  test("home loads and main navigation is visible", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => {
      errors.push(e.message);
    });
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(`console: ${msg.text()}`);
      }
    });

    await stubAssistantTimeline(page);
    await page.goto("/");
    const mainNav = page.getByRole("navigation", { name: "Main navigation" });
    await expect(mainNav).toBeVisible();
    await expect(
      mainNav.getByRole("button", { name: "Eligibility", exact: true })
    ).toBeVisible();
    await expect(
      mainNav.getByRole("button", { name: "Ask AI", exact: true })
    ).toBeVisible();
    await expect(page.getByRole("region", { name: /voter journey/iu })).toBeVisible();
    expect(errors, `client errors: ${errors.join("; ")}`).toEqual([]);
  });

  test("user can open each of the seven journey stages", async ({ page }) => {
    await stubAssistantTimeline(page);
    await page.goto("/");
    const nav = page.getByRole("navigation", { name: "Main navigation" });
    const stages = [
      "Eligibility",
      "Register",
      "Candidates",
      "Manifestos",
      "Booth Finder",
      "Vote-day Prep",
      "Ask AI",
    ] as const;
    for (const name of stages) {
      await nav.getByRole("button", { name, exact: true }).click();
      await expect(nav.getByRole("button", { name, exact: true })).toHaveClass(
        /active/
      );
    }
  });

  test("no critical a11y violations on landing (axe)", async ({ page }) => {
    await stubAssistantTimeline(page);
    await page.goto("/");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
  });
});
