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
});
