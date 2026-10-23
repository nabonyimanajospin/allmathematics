import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

/** A fingerprint of what is drawn on the canvas, to see that something changed (or did not). */
async function fingerprint(page: Page): Promise<number> {
  return page.evaluate(() => {
    const c = document.querySelector("canvas")!;
    const d = c.getContext("2d")!.getImageData(0, 0, c.width, c.height).data;
    let h = 0;
    for (let i = 0; i < d.length; i += 37) h = (h * 31 + d[i]!) | 0;
    return h;
  });
}

async function paintedPixels(page: Page): Promise<number> {
  return page.evaluate(() => {
    const c = document.querySelector("canvas")!;
    const d = c.getContext("2d")!.getImageData(0, 0, c.width, c.height).data;
    const colors = new Set<number>();
    for (let i = 0; i < d.length; i += 4) colors.add((d[i]! << 16) | (d[i + 1]! << 8) | d[i + 2]!);
    return colors.size;
  });
}

test.describe("the grapher", () => {
  test("draws, moves, zooms, makes sliders from letters and reports a bad expression", async ({ page }) => {
    await page.goto("/graph");
    await expect(page.getByRole("heading", { name: "Grapher", level: 1 })).toBeVisible();
    // no account is needed; the two starting expressions are drawn and the letter a is a slider
    await expect(page.getByLabel("Expression 1")).toHaveValue("y = sin(x)");
    await expect(page.getByRole("slider", { name: "a" })).toBeVisible();
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(5);

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // the slider changes the curve
    const before = await fingerprint(page);
    await page.getByRole("slider", { name: "a" }).fill("3");
    await expect.poll(() => fingerprint(page)).not.toBe(before);

    // an implicit curve and a point can be added
    await page.getByRole("button", { name: "Add an expression" }).click();
    await page.getByLabel("Expression 3").fill("x^2 + y^2 = 4");
    const withCircle = await fingerprint(page);
    expect(withCircle).not.toBe(before);

    // zoom and move from the keyboard
    await page.locator("canvas").focus();
    await page.keyboard.press("+");
    await expect.poll(() => fingerprint(page)).not.toBe(withCircle);
    const zoomed = await fingerprint(page);
    await page.keyboard.press("ArrowRight");
    await expect.poll(() => fingerprint(page)).not.toBe(zoomed);
    await page.keyboard.press("Home");

    // a wrong expression is explained, and the other lines stay drawn
    await page.getByLabel("Expression 3").fill("y = foo(x)");
    await expect(page.getByText(/Unknown function foo/)).toBeVisible();
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(5);

    // dragging the picture moves it
    const box = (await page.locator("canvas").boundingBox())!;
    const start = await fingerprint(page);
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 + 80, box.y + box.height / 2 + 40, { steps: 5 });
    await page.mouse.up();
    await expect.poll(() => fingerprint(page)).not.toBe(start);
  });

  test("the 3D view draws a surface, turns when dragged and has no accessibility violations", async ({ page }) => {
    await page.goto("/graph");
    await page.getByRole("tab", { name: "3D surface" }).click();
    await expect(page.getByLabel("Surface z = f(x, y)")).toHaveValue("z = sin(x)*cos(y)");
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(20);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    const before = await fingerprint(page);
    await page.locator("canvas").scrollIntoViewIfNeeded();
    const box = (await page.locator("canvas").boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 + 120, box.y + box.height / 2 - 30, { steps: 6 });
    await page.mouse.up();
    await expect.poll(() => fingerprint(page)).not.toBe(before);

    await page.getByLabel("Surface z = f(x, y)").fill("z = a*(x^2 - y^2)");
    await expect(page.getByRole("slider", { name: "a" })).toBeVisible();
    await page.getByLabel("Space curve (optional)").fill("(cos(t), sin(t), t/3), t in [0, 12]");
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(20);
    await page.getByLabel("Space curve (optional)").fill("(cos(t), sin(t))");
    await expect(page.getByText(/Write the curve as/)).toBeVisible();
  });

  test("fits a phone screen", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 800 });
    await page.goto("/graph");
    await expect(page.locator("canvas")).toBeVisible();
    const scroll = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(scroll).toBeLessThanOrEqual(1);
  });
});
