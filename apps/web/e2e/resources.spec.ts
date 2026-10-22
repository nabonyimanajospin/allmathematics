import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("resources", () => {
  test("lists documents, downloads a permitted one and refuses the others", async ({ page, request }) => {
    await page.goto("/resources");
    await expect(page.getByRole("heading", { name: "Resources", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: "Download" }).first()).toBeVisible();
    await expect(page.getByText("Advanced Engineering Mathematics")).toBeVisible();
    await expect(page.getByText("Not available for download yet.").first()).toBeVisible();

    const ok = await request.get("/resources/download/integral-table");
    expect(ok.status()).toBe(200);
    expect(ok.headers()["content-type"]).toContain("application/pdf");
    expect(ok.headers()["content-disposition"]).toContain("attachment");

    expect((await request.get("/resources/download/book-zill")).status()).toBe(404);
    expect((await request.get("/resources/download/..%2F..%2Fpackage.json")).status()).toBe(404);
  });

  test("the page has no accessibility violations and fits the screen", async ({ page }) => {
    await page.goto("/resources");
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
});
