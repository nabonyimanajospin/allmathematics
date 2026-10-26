import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

const unique = () => `triangle${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

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

test.describe("the triangle toolkit", () => {
  test("is part of the account: a visitor is sent to sign in", async ({ page }) => {
    await page.goto("/triangle");
    await expect(page).toHaveURL(/\/signin/);
  });

  test("gives every value exactly for the triangle A(-2,2), B(-2,-1), C(2,2)", async ({ page }) => {
    await signUp(page);
    await page.goto("/triangle");
    await page.getByRole("button", { name: "Calculate" }).click();
    const result = page.getByTestId("triangle-result");
    await expect(result).toBeVisible();

    // sides, area, perimeter, kind
    await expect(result.getByText("Side BC (longest side)")).toBeVisible();
    await expect(result.getByText("Scalene (three different sides); right (one right angle)")).toBeVisible();
    // the centers and radii: G, I, O, and R, exactly
    await expect(tex(page, String.raw`\left(- \dfrac{2}{3},\,1\right)`).first()).toBeAttached();
    await expect(tex(page, String.raw`\left(-1,\,1\right)`).first()).toBeAttached();
    await expect(tex(page, String.raw`\left(0,\,\dfrac{1}{2}\right)`).first()).toBeAttached();
    await expect(tex(page, String.raw`\dfrac{5}{2}`).first()).toBeAttached();
    // the circles
    await expect(tex(page, String.raw`\left(x+1\right)^{2}+\left(y-1\right)^{2}=1`)).toBeAttached();
    await expect(tex(page, String.raw`x^{2}+\left(y-\dfrac{1}{2}\right)^{2}=\dfrac{25}{4}`)).toBeAttached();

    // the eight equations of the side BC
    await result.getByText("Side BC", { exact: true }).first().click();
    for (const form of ["3x-4y+2=0", String.raw`y=\dfrac{3}{4}x+\dfrac{1}{2}`, String.raw`r\left(3\cos\theta-4\sin\theta\right)+2=0`]) {
      await expect(tex(page, form).first()).toBeAttached();
    }
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

  test("reads a decimal as an exact fraction and explains a mistake", async ({ page }) => {
    await signUp(page);
    await page.goto("/triangle");
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

  test("fits a phone screen without sideways scrolling", async ({ page, isMobile }) => {
    test.skip(!isMobile, "only meaningful on the phone layout");
    await signUp(page);
    await page.goto("/triangle");
    await vertex(page, "A", "-3", "2");
    await vertex(page, "B", "1", "5");
    await vertex(page, "C", "5", "-7");
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("triangle-result")).toBeVisible();
    await page.getByText("Bisector of the angle at A").click(); // the line with radicals is the widest
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
});
