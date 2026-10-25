import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("how progress is counted", () => {
  test("a visitor can read how the percentages are computed, with the example worked out by the real formula", async ({ page }) => {
    await page.goto("/how-progress-works");
    await expect(page.getByRole("heading", { name: "How your progress is counted", level: 1 })).toBeVisible();
    await expect(page.getByText("its sections count 40 points and its exercises count 20 points")).toBeVisible();
    await expect(page.getByText("= 47/60, shown as 78%")).toBeVisible();
    await expect(page.getByText("from 10 to 20 seconds of active reading")).toBeVisible();
    await expect(page.getByText("A unit is 80% the average of its lessons, plus 20% when you pass its test")).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
});
