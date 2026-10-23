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

  test("shows ten typed questions without answers, scores wrong answers as not passed and offers a new attempt", async ({ page }) => {
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
    // no answer key, no hints and no choices in what the browser receives
    expect(startBody).not.toContain('"answer"');
    expect(startBody).not.toContain("solution");
    expect(startBody).not.toContain("hints");
    expect(startBody).not.toContain("multiple_choice");
    await expect(page.getByText("Answered 0 of 10")).toBeVisible();

    for (let i = 0; i < 10; i++) await page.locator(`#q${i}`).fill("12345");
    await expect(page.getByText("Answered 10 of 10")).toBeVisible();
    await page.getByRole("button", { name: "Submit the test" }).click();
    await expect(page.getByRole("status")).toContainText("0 out of 10");
    await expect(page.getByText(/Not passed yet: you need 7 correct answers/)).toBeVisible();
    await expect(page.getByText("Worked solution").first()).toBeVisible();

    await page.getByRole("button", { name: "Try again with new questions" }).click();
    await expect(page.getByText("Answered 0 of 10")).toBeVisible();

    // the dashboard now shows the attempt and the unit is not complete
    await page.goto("/dashboard");
    await expect(page.getByText("Best 0/10").first()).toBeVisible();
  });
});
