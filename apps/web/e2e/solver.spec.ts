import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

const unique = () => `sv${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Solver Fan");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, "mvc");
}

async function solve(page: Page, problem: string): Promise<void> {
  await page.getByLabel("Your problem").fill(problem);
  await page.getByRole("button", { name: "Solve", exact: true }).click();
}

test.describe("the solver", () => {
  test("solves step by step, refuses what it cannot read, and the free plan has a daily limit", async ({ page }) => {
    await signUp(page);
    await page.goto("/solver");
    await expect(page.getByRole("heading", { name: "Solver", level: 1 })).toBeVisible();
    await expect(page.getByText("Free plan: 5 of 5 solves left today")).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    await solve(page, "derivative of x^2*sin(x)");
    await expect(page.getByRole("heading", { name: "Step by step" })).toBeVisible();
    await expect(page.getByText("Product rule").first()).toBeVisible();
    await expect(page.locator("p.font-mono")).toHaveText("x*(x*cos(x) + 2*sin(x))");
    await expect(page.getByText("Free plan: 4 of 5 solves left today")).toBeVisible();

    // a problem that cannot be read does not use up a solve
    await solve(page, "hello world");
    await expect(page.locator("p[role=alert]")).toHaveText("Check the input.");
    await expect(page.getByText(/I could not read/)).toBeVisible();
    await expect(page.getByText("Free plan: 4 of 5 solves left today")).toBeVisible();

    // the equation solver finds both solutions
    await solve(page, "solve x^2=2x for x");
    await expect(page.locator("p.font-mono")).toHaveText("x=0, x=2");

    await solve(page, "x+y=5, x-y=1, x=");
    await expect(page.locator("p[role=alert]")).toHaveText("Check the input.");

    await solve(page, "integral of x*e^x from 0 to 1");
    await expect(page.getByText("Integration by parts").first()).toBeVisible();
    await expect(page.locator("p.font-mono")).toHaveText("1");
    await solve(page, "limit of sin(x)/x as x->0");
    await expect(page.getByText("Free plan: 1 of 5 solves left today")).toBeVisible();
    await solve(page, "norm of (3,4)");
    await expect(page.getByText("Free plan: 0 of 5 solves left today")).toBeVisible();

    // the limit is reached
    await expect(page.getByRole("button", { name: "Solve", exact: true })).toBeDisabled();
    await expect(page.getByText("Online payment is not set up yet.")).toBeVisible();

    // without payment settings there is no checkout, and the webhook refuses everyone
    const origin = new URL(page.url()).origin;
    expect((await page.request.post("/api/payments/checkout", { headers: { origin } })).status()).toBe(503);
    expect((await page.request.post("/api/payments/webhook", { data: { event: "charge.completed" } })).status()).toBe(503);
  });

  test("solves multivariable problems: partial derivatives, extrema, Lagrange, double and line integrals", async ({ page }) => {
    await signUp(page);
    await page.goto("/solver");
    const answer = page.locator("p.font-mono");
    const noBrokenMath = async () => expect(await page.locator(".katex-error").count()).toBe(0);

    await solve(page, "partial derivative of x^2*y + y^3 wrt y at (1, 2)");
    await expect(answer).toHaveText("13");
    await noBrokenMath();

    await solve(page, "critical points of x^3 - 3*x*y + y^3");
    await expect(answer).toHaveText("(0, 0): saddle point, f = 0; (1, 1): local minimum, f = -1");
    await expect(page.getByText("Second-derivative test").first()).toBeVisible();
    await noBrokenMath();

    await solve(page, "maximize x + y subject to x^2 + y^2 = 1");
    await expect(answer).toHaveText("maximum sqrt(2) at (sqrt(2)/2, sqrt(2)/2)");
    await noBrokenMath();

    await solve(page, "double integral of x^2 + y^2 in polar coordinates over r from 0 to 2, theta from 0 to 2*pi");
    await expect(answer).toHaveText("8*pi");
    await expect(page.getByText("checked by numerical integration").first()).toBeVisible();
    await noBrokenMath();

    await solve(page, "line integral of (-y, x) along (cos(t), sin(t)) for t from 0 to 2*pi");
    await expect(answer).toHaveText("2*pi");
    await noBrokenMath();

  });

  test("the operation list has multivariable calculus, and bad limits are refused", async ({ page }) => {
    await signUp(page);
    await page.goto("/solver");
    const answer = page.locator("p.font-mono");
    const noBrokenMath = async () => expect(await page.locator(".katex-error").count()).toBe(0);
    await page.getByLabel("What do you want to do?").selectOption("multivariable");
    await solve(page, "gradient of x^2*y + z at (1,2,3)");
    await expect(answer).toHaveText("(4, 1, 1)");
    await noBrokenMath();
    await solve(page, "double integral of x*y over x from 0 to y, y from 0 to x");
    await expect(page.locator("p[role=alert]")).toHaveText("Check the input.");
  });

  test("matrices, inequalities, tangents, series and areas, chosen from the written examples", async ({ page }) => {
    await signUp(page);
    await page.goto("/solver");
    const answer = page.locator("p.font-mono");
    const noBrokenMath = async () => expect(await page.locator(".katex-error").count()).toBe(0);

    // the examples are grouped and can be touched to fill the box
    await page.getByText("How to write a problem").click();
    await expect(page.getByRole("heading", { name: "Matrices and vectors" })).toBeVisible();
    await page.getByRole("button", { name: "determinant of [[2,1,0],[1,3,1],[0,1,4]]" }).click();
    await expect(page.getByLabel("Your problem")).toHaveValue("determinant of [[2,1,0],[1,3,1],[0,1,4]]");
    await page.getByRole("button", { name: "Solve", exact: true }).click();
    await expect(answer).toHaveText("18");
    await noBrokenMath();

    await solve(page, "solve (x-1)/(x+2) > 0");
    await expect(answer).toHaveText("(-oo, -2) U (1, oo)");
    await noBrokenMath();

    await solve(page, "tangent line to y = x^3 at x = 2");
    await expect(answer).toHaveText("y = 12*x - 16");
    await noBrokenMath();

    await solve(page, "eigenvalues and eigenvectors of [[4,1],[2,3]]");
    await expect(answer).toHaveText("λ = 2: [-1, 2]; λ = 5: [1, 1]");
    await noBrokenMath();

    await solve(page, "sum of 1/n^2 for n from 1 to infinity");
    await expect(answer).toHaveText("pi^2/6");
    await noBrokenMath();
  });

  test("a matrix problem with the wrong sizes is refused with the reason", async ({ page }) => {
    await signUp(page);
    await page.goto("/solver");
    await solve(page, "[[1,2],[3,4]] * [[1,2,3]]");
    await expect(page.locator("p[role=alert]")).toHaveText("Check the input.");
    await expect(page.getByText(/needs as many columns/)).toBeVisible();
  });
});
