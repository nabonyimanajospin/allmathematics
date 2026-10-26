import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

const unique = () => `gr${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUpAndOpen(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Grapher Fan");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "geo");
  await page.goto("/graph");
}


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
  test("is part of the account: a visitor is sent to sign in", async ({ page }) => {
    await page.goto("/graph");
    await expect(page).toHaveURL(/\/signin/);
    const res = await page.request.post("/api/graph/exact", { data: { lines: {}, params: {}, candidates: [] }, headers: { origin: new URL(page.url()).origin } });
    expect(res.status()).toBe(401);
  });

  test("named points, the segment tool and measurements, and moving a point", async ({ page }) => {
    await signUpAndOpen(page);
    await page.getByLabel("Expression 1").fill("A(0, 0)");
    await page.getByLabel("Expression 2").fill("B = (2, 1)");
    await expect(page.locator("p[role=alert]")).toHaveCount(0);
    const canvas = page.locator("canvas");
    /** A place on the picture, in pixels from its centre (50 px per unit); measured fresh, because the page scrolls when buttons are touched. */
    const at = async (dx: number, dy: number): Promise<[number, number]> => {
      await canvas.scrollIntoViewIfNeeded();
      let box = (await canvas.boundingBox())!;
      for (let i = 0; i < 20; i++) {
        await page.waitForTimeout(150);
        const next = (await canvas.boundingBox())!;
        if (next.width === box.width && next.height === box.height && next.y === box.y) break;
        box = next;
      }
      return [box.x + box.width / 2 + dx, box.y + box.height / 2 + dy];
    };
    const touch = async (dx: number, dy: number) => {
      const [x, y] = await at(dx, dy);
      await page.mouse.click(x, y);
    };

    // the segment tool: touch A, then B (scale 50 px per unit: B is 100 px right and 50 px up)
    await page.getByRole("radio", { name: "Segment" }).click();
    await touch(0, 0);
    await expect(page.getByText("First point A chosen")).toBeVisible();
    await touch(100, -50);
    await expect(page.getByLabel("Expression 3")).toHaveValue("segment(A, B)");
    await expect(page.getByText("Segment AB")).toBeVisible();
    await expect(page.getByText("length: √5 lu")).toBeVisible();
    await expect(page.getByText("midpoint: (1, 1/2)")).toBeVisible();
    await expect(page.getByText("equation: y = (1/2)x")).toBeVisible();

    // the point tool puts a point on the nearest whole number and names it: a touch a little off the grid still gives (3, 0)
    await page.getByRole("radio", { name: "Point" }).click();
    await touch(143, 8);
    await expect(page.getByLabel("Expression 4")).toHaveValue("C = (3, 0)");

    // the line tool through two points, and touching an empty place makes a point
    await page.getByRole("radio", { name: "Line" }).click();
    await touch(150, 0);
    await touch(-100, 100);
    await expect(page.getByLabel("Expression 5")).toHaveValue("D = (-2, -2)");
    await expect(page.getByLabel("Expression 6")).toHaveValue("line(C, D)");
    await expect(page.getByText("Line CD")).toBeVisible();

    // the move tool drags a point and the segment follows
    await page.getByRole("radio", { name: "Move" }).click();
    const [fromX, fromY] = await at(100, -50);
    await page.mouse.move(fromX, fromY);
    await page.mouse.down();
    await page.mouse.move(fromX, fromY - 50, { steps: 5 });
    await page.mouse.up();
    await expect(page.getByLabel("Expression 2")).toHaveValue("B = (2, 2)");
    await expect(page.getByText(/length: 2√2 lu/)).toBeVisible();

    // the help lists what can be typed; touching an example puts it in a line
    await page.getByText("What can I type?").click();
    await page.getByRole("button", { name: "r = 1 + cos(theta)" }).click();
    await expect(page.locator("input[aria-label^=Expression]").last()).toHaveValue("r = 1 + cos(theta)");

    // a point that is not defined is explained
    await page.getByRole("button", { name: "Add an expression" }).click();
    await page.getByLabel("Expression 8").fill("segment(A, Z)");
    await expect(page.getByText(/The point Z is not defined/)).toBeVisible();
  });

  test("draws, moves, zooms, makes sliders from letters and reports a bad expression", async ({ page }) => {
    await signUpAndOpen(page);
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

  test("shades an inequality, lists roots and intersections, and a copied link restores the graph", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]).catch(() => undefined);
    await signUpAndOpen(page);
    await page.getByLabel("Expression 1").fill("y = x^2 - 4");
    await page.getByLabel("Expression 2").fill("y = x - 2");
    await expect(page.getByRole("heading", { name: "Roots and intersections" })).toBeVisible();
    // the engine makes them exact; the TeX of each exact point is in the page
    const tex = (src: string) => page.locator("annotation").filter({ hasText: src });
    await expect(page.getByText("Line 1 crosses the x-axis:")).toBeVisible();
    await expect(tex(String.raw`\left(-2,\ 0\right)`).first()).toBeAttached();
    await expect(tex(String.raw`\left(2,\ 0\right)`).first()).toBeAttached();
    await expect(tex(String.raw`\left(-1,\ -3\right)`).first()).toBeAttached();

    // exact radicals and multiples of pi, not decimals
    await page.getByLabel("Expression 1").fill("y = x^2 - 2");
    await page.getByLabel("Expression 2").fill("y = sin(x)");
    await expect(tex(String.raw`\sqrt{2}`).first()).toBeAttached();
    await expect(tex(String.raw`\pi`).first()).toBeAttached();
    // a value with no closed form stays a decimal and says so
    await page.getByLabel("Expression 1").fill("y = cos(x)");
    await page.getByLabel("Expression 2").fill("y = x");
    await expect(page.getByText(/≈ \(0\.7391, 0\.7391\)/)).toBeVisible();
    await page.getByLabel("Expression 1").fill("y = x^2 - 4");
    await page.getByLabel("Expression 2").fill("y = x - 2");

    const before = await paintedPixels(page);
    await page.getByRole("button", { name: "Add an expression" }).click();
    await page.getByLabel("Expression 3").fill("x^2 + y^2 <= 4");
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(before);
    await page.getByLabel("Expression 3").fill("y < x < 3");
    await expect(page.getByText(/Use one inequality sign/)).toBeVisible();
    await page.getByLabel("Expression 3").fill("x^2 + y^2 <= 4");

    await page.getByRole("button", { name: "Copy link" }).click();
    const link = await page.evaluate(() => navigator.clipboard.readText()).catch(() => null);
    if (link) {
      await page.goto(link);
      await page.reload();
      await expect(page.getByLabel("Expression 3")).toHaveValue("x^2 + y^2 <= 4");
      await expect(page.getByLabel("Expression 1")).toHaveValue("y = x^2 - 4");
    }
  });

  test("circles, polygons and slope fields with exact measurements, and a parametric surface", async ({ page }) => {
    await signUpAndOpen(page);
    const rows: string[] = ["A(0, 0)", "B(3, 4)", "circle(A, B)", "C(6, 0)", "polygon(A, B, C)", "ode(y' = x - y, A)"];
    for (let i = 0; i < rows.length; i++) {
      if (i >= 2) await page.getByRole("button", { name: "Add an expression" }).click();
      await page.getByLabel(`Expression ${i + 1}`).fill(rows[i]!);
    }
    await expect(page.locator("p[role=alert]")).toHaveCount(0);
    await expect(page.getByText("Circle with centre A through B")).toBeVisible();
    await expect(page.getByText("radius: 5 lu")).toBeVisible();
    await expect(page.getByText("circumference: 10π")).toBeVisible();
    await expect(page.getByText("area: 25π squ")).toBeVisible();
    await expect(page.getByText("equation: x² + y² = 25")).toBeVisible();
    await expect(page.getByText("Polygon ABC")).toBeVisible();
    await expect(page.getByText("perimeter: 16 lu")).toBeVisible();
    await expect(page.getByText("area: 12 squ")).toBeVisible();
    expect(await paintedPixels(page)).toBeGreaterThan(5);

    // an unknown point is explained, for a circle and for a differential equation
    await page.getByRole("button", { name: "Add an expression" }).click();
    await page.getByLabel("Expression 7").fill("circle(A, Z)");
    await expect(page.getByText(/The point Z is not defined/)).toBeVisible();
    await page.getByLabel("Expression 7").fill("polygon(A, B)");
    await expect(page.getByText(/at least three named points/)).toBeVisible();

    // 3D: a ready-made parametric surface
    await page.getByRole("tab", { name: "3D surface" }).click();
    await page.getByRole("button", { name: "Sphere", exact: true }).click();
    await expect(page.getByLabel("Surface z = f(x, y)")).toHaveValue(/^\(3\*sin\(u\)\*cos\(v\)/);
    await expect(page.locator("p[role=alert]")).toHaveCount(0);
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(20);
    await page.getByRole("button", { name: "Torus", exact: true }).click();
    await expect(page.locator("p[role=alert]")).toHaveCount(0);
    await expect.poll(() => paintedPixels(page)).toBeGreaterThan(20);
  });

  test("the 3D view draws a surface, turns when dragged and has no accessibility violations", async ({ page }) => {
    await signUpAndOpen(page);
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
    await signUpAndOpen(page);
    await expect(page.locator("canvas")).toBeVisible();
    const scroll = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(scroll).toBeLessThanOrEqual(1);
  });
});
