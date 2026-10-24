import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

const UNIT = "geo-m01-u01";
const unique = () => `ut${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Unit Tester");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "geo");
}

test.describe("the unit test", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => window.localStorage.setItem("answer-mode", "text"));
  });

  test("shows ten questions (at most 3 multiple choice) without answers, does not pass wrong answers and offers a new attempt", async ({ page }) => {
    await signUp(page);
    // the dashboard offers the test of the unit
    await expect(page.getByText("Not taken yet").first()).toBeVisible();
    await page.goto(`/test/${UNIT}`);
    await expect(page.getByRole("heading", { name: /Unit test:/, level: 1 })).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    const started = page.waitForResponse((r) => r.url().endsWith("/api/unit-tests") && r.request().method() === "POST");
    await page.getByRole("button", { name: "Start the test" }).click();
    const startBody = await (await started).text();
    // no answer key, no hints and no number of the right choice in what the browser receives
    expect(startBody).not.toContain('"answer"');
    expect(startBody).not.toContain("solution");
    expect(startBody).not.toContain("hints");
    expect(startBody).not.toContain("correctIndex");
    await expect(page.getByText("Answered 0 of 10")).toBeVisible();

    // at most 3 multiple-choice questions; the others are typed
    const groups = page.getByRole("group", { name: "Choose one answer" });
    const choiceCount = await groups.count();
    expect(choiceCount).toBeGreaterThanOrEqual(1);
    expect(choiceCount).toBeLessThanOrEqual(3);
    for (let i = 0; i < 10; i++) {
      const typed = page.locator(`#q${i}`);
      if (await typed.count()) await typed.fill("12345");
      else await page.locator(`input[name="q${i}-choice"]`).first().check();
    }
    await expect(page.getByText("Answered 10 of 10")).toBeVisible();
    await page.getByRole("button", { name: "Submit the test" }).click();
    // a typed answer of 12345 is wrong everywhere; only a lucky choice can score, and never 7
    await expect(page.getByRole("status")).toContainText(/^[0-3] out of 10/);
    await expect(page.getByText(/Not passed yet: you need 7 correct answers/)).toBeVisible();
    await expect(page.getByText("Worked solution").first()).toBeVisible();

    await page.getByRole("button", { name: "Try again with new questions" }).click();
    await expect(page.getByText("Answered 0 of 10")).toBeVisible();

    // the dashboard now shows the attempt and the unit is not complete
    await page.goto("/dashboard");
    await expect(page.getByText(/Best [0-3]\/10/).first()).toBeVisible();

    // the test is also in the course outline beside the lessons of the unit
    await page.goto("/learn/geo-m01-u01-l01");
    await expect(page.locator(`a[href="/test/${UNIT}"]`).first()).toHaveCount(1);
  });
});
