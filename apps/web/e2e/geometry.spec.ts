import AxeBuilder from "@axe-core/playwright";
import { enrollAfterSignUp } from "./helpers";
import { expect, test, type Page } from "@playwright/test";

// Lessons with wide tables and long formulas: the eight equations of a line, the triangle, the tetrahedron.
const LESSONS = ["geo-m02-u01-l02", "geo-m02-u02-l01", "geo-m02-u02-l07", "geo-m03-u02-l04"];
const unique = () => `geo${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Geometry Tester");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "geo");
}

test.describe("geometry lessons", () => {
  test("long formulas and tables fit the screen, with a white page and no accessibility violations", async ({ page }) => {
    await signUp(page);
    for (const id of LESSONS) {
      await page.goto(`/learn/${id}`);
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(overflow, `overflow in ${id}`).toBeLessThanOrEqual(1);
      const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      expect(results.violations.map((v) => `${v.id}: ${v.nodes.length}`), `axe in ${id}`).toEqual([]);
    }
  });

  test("the lesson background is pure white in the light theme", async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem("allmaths-theme", "light"));
    await signUp(page);
    await page.goto(`/learn/${LESSONS[0]}`);
    const background = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    expect(background).toBe("rgb(255, 255, 255)");
  });
});
