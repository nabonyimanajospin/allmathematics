import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const unique = () => `form${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Formula Saver");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");
}

test.describe("formula sheet", () => {
  test("a saved formula appears on the sheet, stays saved after a refresh, and can be removed", async ({ page }) => {
    await signUp(page);
    await page.goto("/formulas");
    await expect(page.getByText("Nothing saved yet")).toBeVisible();

    await page.goto("/learn/geo-m02-u02-l02");
    const save = page.getByRole("button", { name: /Save to my formula sheet/ }).first();
    await save.scrollIntoViewIfNeeded();
    const saving = page.waitForResponse((r) => r.url().includes("/api/formulas") && r.request().method() === "POST");
    await save.click();
    expect((await saving).ok()).toBe(true);
    await expect(page.getByRole("button", { name: /Saved to my formula sheet/ }).first()).toBeVisible();

    await page.reload();
    await expect(page.getByRole("button", { name: /Saved to my formula sheet/ }).first()).toBeVisible();

    await page.goto("/dashboard");
    await page.getByRole("link", { name: "Formula sheet" }).first().click();
    await expect(page.getByRole("heading", { name: "My formula sheet", level: 1 })).toBeVisible();
    await expect(page.getByText("Medians and the centroid").first()).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    await page.getByRole("button", { name: "Remove" }).first().click();
    await expect(page.getByText("Nothing saved yet")).toBeVisible();
  });
});
