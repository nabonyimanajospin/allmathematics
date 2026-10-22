import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const LESSON = "geo-m01-u01-l01";
const unique = () => `e2e${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page, name: string): Promise<string> {
  const email = unique();
  await page.goto("/signup");
  await page.getByLabel("Full name").fill(name);
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");
  return email;
}

const lessonBar = (page: Page) => page.getByRole("progressbar", { name: "Lesson progress" });
const percent = async (page: Page) => Number(await lessonBar(page).getAttribute("aria-valuenow"));

test.describe("student journey (spec Phase 1 acceptance)", () => {
  test.beforeEach(async ({ page }) => {
    // these tests check the server, so they type into the plain-text answer box
    await page.addInitScript(() => window.localStorage.setItem("answer-mode", "text"));
  });

  test("sign up, read, answer: progress moves per section and survives a refresh", async ({ page }) => {
    await signUp(page, "Ada Lovelace");
    await expect(page.getByRole("heading", { name: /Hello, Ada/ })).toBeVisible();

    // open lesson 1 from the dashboard
    await page.getByRole("link", { name: /Start/ }).first().click();
    await page.waitForURL(`**/learn/${LESSON}`);
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Points, coordinates and the vector AB");
    expect(await percent(page)).toBe(0);

    // The first concept section completes after 20 seconds of real reading time (spec 3.3).
    await expect.poll(() => percent(page), { timeout: 60_000, intervals: [1000] }).toBeGreaterThanOrEqual(7);

    // Refresh: the exact progress is still there (it comes from the server, not the browser).
    await page.reload();
    await expect.poll(() => percent(page), { timeout: 20_000 }).toBeGreaterThanOrEqual(7);
    const afterRefresh = await percent(page);
    expect(afterRefresh).toBeGreaterThanOrEqual(7);

    // Answer the first check with an equivalent exact form; the section completes and the bar rises.
    const input = page.getByLabel("Your answer").first();
    await input.scrollIntoViewIfNeeded();
    await input.fill("(3, -4)");
    await page.getByRole("button", { name: "Check", exact: true }).click();
    await expect(page.getByText("Correct.").first()).toBeVisible();
    await expect.poll(() => percent(page)).toBeGreaterThan(afterRefresh);

    await page.reload();
    await expect(page.getByText("Correct.").first()).toBeVisible();
  });

  test("wrong and decimal answers get the right feedback, and the answer key never reaches the browser", async ({ page }) => {
    await signUp(page, "Grace Hopper");
    await page.goto(`/learn/${LESSON}`);

    // nothing in the delivered page reveals the key
    const html = await page.content();
    expect(html).not.toContain("(3, -4)");

    const input = page.getByLabel("Your answer").first();
    await input.scrollIntoViewIfNeeded();

    await input.fill("(-3, 4)");
    await page.getByRole("button", { name: "Check", exact: true }).click();
    await expect(page.getByText("Not correct yet")).toBeVisible();
    await expect(page.getByText(/wrong order|end minus start/i).first()).toBeVisible(); // targeted hint

    await input.fill("(3.0, -4)");
    await page.getByRole("button", { name: "Check", exact: true }).click();
    await expect(page.getByText(/exact value/i)).toBeVisible();

    // hints are revealed one at a time
    await page.getByRole("button", { name: /Show a hint \(1 of 2\)/ }).click();
    await expect(page.getByRole("button", { name: /Show a hint \(2 of 2\)/ })).toBeVisible();
  });

  test("content below an unanswered question stays locked", async ({ page }) => {
    await signUp(page, "Alan Turing");
    await page.goto(`/learn/${LESSON}`);
    await expect(page.getByText("Answer the question above to continue.")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Equal vectors and free vectors" })).toHaveCount(0);
  });

  test("protected pages redirect to sign-in and return afterwards", async ({ page }) => {
    await page.goto(`/learn/${LESSON}`);
    await page.waitForURL(/\/signin\?next=/);
    await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
    await page.getByLabel("E-mail").fill("nobody@example.com");
    await page.getByLabel("Password").fill("wrong password here");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("form [role=alert]")).toContainText("E-mail or password is incorrect");
  });
});

test.describe("quality", () => {
  test("home, sign-in and lesson pages have no detectable accessibility violations (light and dark)", async ({ page }) => {
    for (const theme of ["light", "dark"] as const) {
      await page.addInitScript((t) => localStorage.setItem("allmaths-theme", t), theme);
      await page.goto("/");
      let results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      expect(results.violations, `home ${theme}`).toEqual([]);
      await page.goto("/signin");
      results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      expect(results.violations, `signin ${theme}`).toEqual([]);
    }
    await signUp(page, "Axe Tester");
    await page.goto(`/learn/${LESSON}`);
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(results.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
  });

  test("the lesson page fits a phone screen without horizontal scrolling", async ({ page }) => {
    await signUp(page, "Phone User");
    await page.goto(`/learn/${LESSON}`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
  });

  test("the theme toggle switches and remembers the theme", async ({ page }) => {
    await page.goto("/");
    const toggle = page.getByRole("button", { name: /Colour theme/ });
    await toggle.click(); // automatic -> light
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await toggle.click(); // -> dark
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await page.reload();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  });
});
