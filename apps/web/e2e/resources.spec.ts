import AxeBuilder from "@axe-core/playwright";
import { enrollAfterSignUp } from "./helpers";
import { expect, test, type Page } from "@playwright/test";

const unique = () => `res${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Resource Reader");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "geo");
}

test.describe("resources", () => {
  test("are for signed-in students only", async ({ page, request }) => {
    await page.goto("/resources");
    await page.waitForURL("**/signin**");
    expect((await request.get("/resources/download/integral-table")).status()).toBe(401);
    expect((await request.get("/resources/download/integral-table?inline=1")).status()).toBe(401);
  });

  test("a signed-in student sees size and type, previews, downloads a permitted one and is refused the others", async ({ page }) => {
    await signUp(page);
    await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Resources" }).click();
    await expect(page.getByRole("heading", { name: "Resources", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: "Download" }).first()).toBeVisible();
    await page.getByRole("link", { name: "Preview" }).first().click();
    await expect(page.locator("iframe")).toBeVisible();
    await page.getByRole("link", { name: /Back to resources/ }).click();
    await page.waitForURL("**/resources");
    await expect(page.getByRole("heading", { name: "Resources", level: 1 })).toBeVisible();
    await expect(page.getByText(/PDF · \d/).first()).toBeVisible();
    await expect(page.getByText("Advanced Engineering Mathematics")).toBeVisible();
    await expect(page.getByText("Not available for download yet.").first()).toBeVisible();

    const prev = await page.request.get("/resources/download/integral-table?inline=1");
    expect(prev.status()).toBe(200);
    expect(prev.headers()["content-disposition"]).toContain("inline");
    const ok = await page.request.get("/resources/download/integral-table");
    expect(ok.headers()["content-type"]).toContain("application/pdf");
    expect(ok.headers()["content-disposition"]).toContain("attachment");

    expect((await page.request.get("/resources/download/book-zill")).status()).toBe(404);
    expect((await page.request.get("/resources/download/..%2F..%2Fpackage.json")).status()).toBe(404);
  });

  test("the page has no accessibility violations and fits the screen", async ({ page }) => {
    await signUp(page);
    await page.goto("/resources");
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
});
