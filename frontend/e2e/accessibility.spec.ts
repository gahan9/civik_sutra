import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const STAGES = [
  { name: "Eligibility", region: /voter|eligibility/i },
  { name: "Register", region: /apply|register|epic/i },
  { name: "Candidates", region: /candidate/i },
  { name: "Manifestos", region: /manifesto/i },
  { name: "Booth Finder", region: /booth/i },
  { name: "Vote-day Prep", region: /voter|readiness|checklist/i },
  { name: "Ask AI", region: /ask ai|chat|assistant/i },
] as const;

test.describe("WCAG 2.1 AA accessibility", () => {
  test("landing page has no critical axe violations", async ({ page }) => {
    await page.goto("/");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
  });

  for (const stage of STAGES) {
    test(`${stage.name} stage passes axe scan`, async ({ page }) => {
      await page.goto("/");
      const nav = page.getByRole("navigation", { name: "Main navigation" });
      await nav.getByRole("button", { name: stage.name, exact: true }).click();

      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();

      expect(
        results.violations,
        `${stage.name} a11y violations: ${JSON.stringify(results.violations, null, 2)}`
      ).toEqual([]);
    });
  }

  test("keyboard navigation reaches every primary stage", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation", { name: "Main navigation" });

    const labels: string[] = [
      "Eligibility",
      "Register",
      "Candidates",
      "Manifestos",
      "Booth Finder",
      "Vote-day Prep",
      "Ask AI",
    ];
    for (const label of labels) {
      const button = nav.getByRole("button", { name: label, exact: true });
      await button.focus();
      await expect(button).toBeFocused();
      await page.keyboard.press("Enter");
      await expect(button).toHaveClass(/active/);
    }
  });

  test("language selector works without mouse", async ({ page }) => {
    await page.goto("/");
    const hindiButton = page.getByRole("button", {
      name: /switch to hindi/i,
    });
    await hindiButton.focus();
    await expect(hindiButton).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(hindiButton).toHaveClass(/lang-btn--active/);
  });
});
