import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

// A lesson of Module 4 with an exercise set from the printed sheet.
const LESSON = "mvc-m04-u01-l02";
const unique = () => `ex${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page, name: string): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill(name);
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");
}

/** Exercises appear once the lesson's own check questions are answered: answer the single check of this lesson. */
async function unlockExercises(page: Page): Promise<void> {
  await page.goto(`/learn/${LESSON}`);
  const input = page.getByLabel("Your answer").first();
  await input.scrollIntoViewIfNeeded();
  await input.fill("y = C*e^(x^2)");
  await page.getByRole("button", { name: "Check", exact: true }).first().click();
  await expect(page.getByText("Correct.").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Exercises" })).toBeVisible();
}

test.describe("exercises (the printed sheet inside the lesson)", () => {
  test.beforeEach(async ({ page }) => {
    // these tests check the server, so they type into the plain-text answer box
    await page.addInitScript(() => window.localStorage.setItem("answer-mode", "text"));
  });

  test("an exercise accepts an equivalent exact answer and then shows the worked solution", async ({ page }) => {
    await signUp(page, "Exercise Tester");
    await unlockExercises(page);

    const item = page.locator("#ex-sep-e");
    await item.scrollIntoViewIfNeeded();
    await item.getByLabel("Your answer").fill("y = K sin(x)");
    await item.getByRole("button", { name: "Check", exact: true }).click();
    await expect(item.getByText("Correct.")).toBeVisible();
    await expect(item.getByText(/ln|sin/).first()).toBeVisible();

    // The solved counter moved, and the answer survives a refresh (it is stored on the server).
    await page.reload();
    await expect(page.locator("#ex-sep-e").getByText("Correct.")).toBeVisible();
  });

  test("a wrong answer is not accepted, and no answer key is in the page the browser receives", async ({ page }) => {
    await signUp(page, "Key Tester");
    const html = await (await page.request.get(`/learn/${LESSON}`)).text();
    expect(html).not.toContain("C*sin(x)");
    expect(html).not.toContain("2*ln(1+e^x)");

    await unlockExercises(page);
    const item = page.locator("#ex-sep-e");
    await item.scrollIntoViewIfNeeded();
    await item.getByLabel("Your answer").fill("y = C*cos(x)");
    await item.getByRole("button", { name: "Check", exact: true }).click();
    await expect(item.getByText("Correct.")).toHaveCount(0);
  });

  test("the exercise page fits a phone screen and has no accessibility violations", async ({ page }) => {
    await signUp(page, "Quality Tester");
    await unlockExercises(page);
    for (const theme of ["light", "dark"] as const) {
      await page.addInitScript((t) => localStorage.setItem("allmaths-theme", t), theme);
      await page.goto(`/learn/${LESSON}`);
      await page.locator("#exercises").scrollIntoViewIfNeeded();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(overflow, `overflow ${theme}`).toBeLessThanOrEqual(1);
      const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      expect(results.violations.map((v) => `${v.id}: ${v.nodes.length}`), `axe ${theme}`).toEqual([]);
    }
  });
});
