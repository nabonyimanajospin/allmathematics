import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

const unique = () => `triangle${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;
const TRIANGLE = "/solver?mode=triangle";

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Triangle Tester");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "geo");
}

/** KaTeX keeps the TeX source in an annotation: the tests read the exact value from there. */
const tex = (page: Page, source: string) => page.locator("annotation", { hasText: source });

async function vertex(page: Page, name: string, x: string, y: string): Promise<void> {
  await page.getByLabel(`Vertex ${name}, coordinate x`).fill(x);
  await page.getByLabel(`Vertex ${name}, coordinate y`).fill(y);
}

/** Opens one kind of line and checks that the line is shown with its eight forms. */
async function showLines(page: Page, tab: string, heading: string): Promise<void> {
  await page.getByRole("tab", { name: tab }).click();
  const title = page.getByRole("heading", { name: new RegExp(heading) });
  await expect(title).toBeVisible();
  const card = page.locator("div", { has: title }).last();
  for (const form of ["Vector equation", "Parametric equations", "Symmetric (canonical) equation", "Implicit equation", "Explicit equation", "Normal (Hesse) form", "Polar equation", "Intercept form"]) {
    await expect(card.getByText(form, { exact: true }).first()).toBeVisible();
  }
}

test.describe("the triangle toolkit, inside the solver", () => {
  test("is part of the account: a visitor is sent to sign in, and the old address still leads to it", async ({ page }) => {
    await page.goto("/triangle");
    await expect(page).toHaveURL(/\/signin\?next=.*mode%3Dtriangle/);
  });

  test("has no link of its own in the header: it is a tab of the solver", async ({ page, isMobile }) => {
    test.skip(isMobile, "the header links are on the desktop layout");
    await signUp(page);
    await page.goto("/dashboard");
    const header = page.getByRole("navigation", { name: "Main" });
    await expect(header.getByRole("link", { name: "Solver" })).toBeVisible();
    await expect(header.getByRole("link", { name: "Triangle", exact: true })).toHaveCount(0);
    await page.goto("/solver");
    await expect(page.getByRole("tab", { name: "Any problem" })).toHaveAttribute("aria-selected", "true");
    await page.getByRole("tab", { name: "A triangle (three vertices)" }).click();
    await expect(page.getByLabel("Vertex A, coordinate x")).toBeVisible();
  });

  test("gives every value exactly for the triangle A(-2,2), B(-2,-1), C(2,2)", async ({ page }) => {
    await signUp(page);
    await page.goto(TRIANGLE);
    await page.getByRole("button", { name: "Calculate" }).click();
    const result = page.getByTestId("triangle-result");
    await expect(result).toBeVisible({ timeout: 60_000 }); // the first calculation can wait for the engine to warm up

    // sides, area, perimeter, kind
    await expect(result.getByText("Side BC (longest side)")).toBeVisible();
    await expect(result.getByText("Scalene (three different sides); right (one right angle)")).toBeVisible();
    // the centers and radii: G, I, O, and R, exactly
    await expect(tex(page, String.raw`\left(- \dfrac{2}{3},\,1\right)`).first()).toBeAttached();
    await expect(tex(page, String.raw`\left(-1,\,1\right)`).first()).toBeAttached();
    await expect(tex(page, String.raw`\left(0,\,\dfrac{1}{2}\right)`).first()).toBeAttached();
    await expect(tex(page, String.raw`\dfrac{5}{2}`).first()).toBeAttached();
    // the circles, with the names of the course: canonical equation and analytic implicit equation
    await expect(result.getByText("Canonical equation").first()).toBeVisible();
    await expect(result.getByText("Analytic implicit equation").first()).toBeVisible();
    await expect(tex(page, String.raw`\left(x+1\right)^{2}+\left(y-1\right)^{2}=1`)).toBeAttached();
    await expect(tex(page, "x^{2}+y^{2}+2x-2y+1=0")).toBeAttached();

    // no decimal number is written anywhere in the visible results (the hidden MathML source is left out)
    const visible = await result.evaluate((el) => {
      const copy = el.cloneNode(true) as HTMLElement;
      copy.querySelectorAll(".katex-mathml").forEach((n) => n.remove());
      return copy.textContent ?? "";
    });
    expect(visible).not.toMatch(/\d\.\d/);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test("shows the eight equations of every side, median, altitude, angle bisector and perpendicular bisector", async ({ page }) => {
    await signUp(page);
    await page.goto(TRIANGLE);
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("triangle-result")).toBeVisible({ timeout: 60_000 });

    // the sides are shown first, all open: each side has its eight forms
    await showLines(page, "The sides", "Side BC");
    for (const form of ["3x-4y+2=0", String.raw`y=\dfrac{3}{4}x+\dfrac{1}{2}`, String.raw`r\left(3\cos\theta-4\sin\theta\right)+2=0`, String.raw`\dfrac{x+2}{4}=\dfrac{y+1}{3}`]) {
      await expect(tex(page, form).first()).toBeAttached();
    }
    await showLines(page, "The medians", "Median from A");
    await expect(tex(page, "3x+4y-2=0").first()).toBeAttached();
    await showLines(page, "The altitudes", "Altitude from B");
    await expect(tex(page, "x+2=0").first()).toBeAttached();
    await showLines(page, "The angle bisectors", "Bisector of the angle at C");
    await expect(tex(page, "x-3y+4=0").first()).toBeAttached();
    await showLines(page, "The perpendicular bisectors", "Perpendicular bisector of CA");
    await expect(tex(page, "x=0").first()).toBeAttached();
    // the jump bar leads to the lines
    await expect(page.getByRole("navigation", { name: "Parts of the result" }).getByRole("link", { name: "The lines of the triangle" })).toBeVisible();
  });

  test("reads a decimal as an exact fraction and explains a mistake", async ({ page }) => {
    await signUp(page);
    await page.goto(TRIANGLE);
    await vertex(page, "A", "0", "0");
    await vertex(page, "B", "1/2", "0");
    await vertex(page, "C", "0", "0.25");
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(tex(page, String.raw`\dfrac{1}{16}`).first()).toBeAttached();

    await vertex(page, "C", "1", "0");
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(page.locator("form").getByRole("alert")).toContainText("on one straight line");

    await vertex(page, "C", "sqrt(2)", "1");
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(page.locator("form").getByRole("alert")).toContainText("must be a whole number, a fraction");
  });

  test("the solver notices a triangle problem and offers the toolkit, which analyzes it at once", async ({ page }) => {
    await signUp(page);
    await page.goto("/solver");
    await expect(page.getByText("Is your problem about a triangle?")).toBeVisible();
    const box = page.getByRole("textbox", { name: "Problem" });
    await box.fill("triangle A(0,0), B(4,0), C(0,3)");
    await expect(page.getByText("This looks like a problem about a triangle.")).toBeVisible();
    await page.getByRole("button", { name: "Analyze this triangle" }).click();
    await expect(page.getByRole("tab", { name: "A triangle (three vertices)" })).toHaveAttribute("aria-selected", "true");
    await expect(page.getByLabel("Vertex C, coordinate y")).toHaveValue("3");
    const result = page.getByTestId("triangle-result");
    await expect(result).toBeVisible({ timeout: 60_000 });
    await expect(result.getByText("Side BC (longest side)")).toBeVisible();
    await expect(tex(page, String.raw`\left(2,\,\dfrac{3}{2}\right)`).first()).toBeAttached(); // the circumcenter of the 3-4-5 triangle
    // what was typed before is still there when the learner goes back
    await page.getByRole("tab", { name: "Any problem" }).click();
    await expect(box).toHaveValue("triangle A(0,0), B(4,0), C(0,3)");
  });

  test("fits a phone screen without sideways scrolling", async ({ page, isMobile }) => {
    test.skip(!isMobile, "only meaningful on the phone layout");
    await signUp(page);
    await page.goto(TRIANGLE);
    await vertex(page, "A", "-3", "2");
    await vertex(page, "B", "1", "5");
    await vertex(page, "C", "5", "-7");
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("triangle-result")).toBeVisible({ timeout: 60_000 });
    await page.getByRole("tab", { name: "The angle bisectors" }).click(); // the lines with radicals are the widest
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
});
