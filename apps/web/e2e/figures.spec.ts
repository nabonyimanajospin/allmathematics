import AxeBuilder from "@axe-core/playwright";
import { enrollAfterSignUp } from "./helpers";
import { expect, test, type Page } from "@playwright/test";

const unique = () => `fig${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Figure Reader");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "geo");
}

test.describe("geometry figures", () => {
  test("the centroid lesson shows its figure and the formula before the first question", async ({ page }) => {
    await signUp(page);
    await page.goto("/learn/geo-m02-u02-l02");
    const figure = page.getByRole("img", { name: /three medians/ });
    await expect(figure).toBeVisible();
    await expect(page.getByText("the intersection point of the medians")).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test("a 3D figure turns when it is dragged", async ({ page }) => {
    await signUp(page);
    await page.goto("/learn/geo-m03-u02-l01");
    const figure = page.getByRole("img", { name: /tetrahedron in space/ });
    await figure.scrollIntoViewIfNeeded();
    const before = await figure.innerHTML();
    const box = (await figure.boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 + 80, box.y + box.height / 2 + 20, { steps: 5 });
    await page.mouse.up();
    expect(await figure.innerHTML()).not.toBe(before);
    await page.getByRole("button", { name: "Reset the view" }).click();
    expect(await figure.innerHTML()).toBe(before);
  });
});
