import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

// A lesson with a long explanation behind "Explain this in more detail" before its first check question.
const LESSON = "geo-m02-u01-l02";
const unique = () => `outline${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Outline Tester");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");
}

test.describe("course outline and explanations", () => {
  test("the outline lists the modules and lessons of the course and opens another lesson", async ({ page, isMobile }) => {
    await signUp(page);
    await page.goto(`/learn/${LESSON}`);
    if (isMobile) await page.getByText("Open the course outline").click();
    const nav = page.getByRole("navigation", { name: "Course outline" }).filter({ visible: true });
    await expect(nav.getByText("Geometry of the plane")).toBeVisible();
    await expect(nav.getByRole("link", { name: /The eight equations of a straight line/ })).toHaveAttribute("aria-current", "page");
    await nav.getByRole("searchbox").fill("circumcircle");
    await expect(nav.getByRole("link", { name: /circumcircle/i }).first()).toBeVisible();
    await nav.getByRole("link", { name: /circumcircle/i }).first().click();
    await page.waitForURL("**/learn/geo-m02-u02-l06");
  });

  test("a longer explanation stays hidden until the student asks for it", async ({ page }) => {
    await signUp(page);
    await page.goto(`/learn/${LESSON}`);
    const more = page.getByText("Explain this in more detail").first();
    await more.scrollIntoViewIfNeeded();
    await expect(page.getByText("Why the sign rule?")).toBeHidden();
    await more.click();
    await expect(page.getByText("Why the sign rule?")).toBeVisible();
  });

  test("a worked example explains how a step was found when asked", async ({ page }) => {
    await signUp(page);
    await page.goto(`/learn/${LESSON}`);
    const example = page.locator("[data-section=ex-eight]");
    await example.scrollIntoViewIfNeeded();
    await example.getByRole("button", { name: "Show all steps" }).click();
    await expect(example.getByText("We want x cos").first()).toBeHidden();
    await example.getByText("How was this step found?").first().click();
    await expect(example.getByText(/divide by \$?-?5|We divide by/).first()).toBeVisible();
  });

  test("the page with the outline has no accessibility violations", async ({ page }) => {
    await signUp(page);
    await page.goto(`/learn/${LESSON}`);
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(results.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
  });
});
