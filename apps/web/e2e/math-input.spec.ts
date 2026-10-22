import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const LESSON = "geo-m01-u01-l01";
const unique = () => `mi${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Math Writer");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");
}

test.describe("answer field", () => {
  test("a fraction typed with a slash is shown stacked and sent as an exact quotient", async ({ page }) => {
    await signUp(page);
    await page.goto(`/learn/${LESSON}`);
    const field = page.locator("math-field").first();
    await field.scrollIntoViewIfNeeded();
    // the field is a web component that loads on demand: wait until it can be written in
    await expect.poll(() => field.evaluate((el) => typeof (el as unknown as { getValue?: unknown }).getValue === "function")).toBe(true);
    await field.click();
    await page.keyboard.type("2/3");
    // a numerator over a denominator, not a slash
    await expect(field.locator(".ML__mfrac, .ML__frac").first()).toBeVisible();
    expect(await field.evaluate((el) => (el as unknown as { getValue(f: string): string }).getValue("latex"))).toBe("\\frac23");
    await expect(page.getByRole("button", { name: "Fraction" }).first()).toBeVisible();
  });

  test("the plain-text box stays available and the page has no accessibility violations", async ({ page }) => {
    await signUp(page);
    await page.goto(`/learn/${LESSON}`);
    await page.locator("math-field").first().scrollIntoViewIfNeeded();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
    await page.getByRole("button", { name: "Type as plain text instead" }).first().click();
    await expect(page.getByLabel("Your answer").first()).toBeVisible();
  });
});
