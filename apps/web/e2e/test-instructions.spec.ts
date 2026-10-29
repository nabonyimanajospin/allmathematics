import { expect, test } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

// Its practice sets are such as "Find the domain of definition of each function.": the statement of an exercise is then only a function.
const UNIT = "mvc-m01-u01";

test.describe("a unit test of the multivariable course", () => {
  test("shows what to do with every question, not only an equation", async ({ page }) => {
    await page.goto("/signup");
    await page.getByLabel("Full name").fill("Instruction Tester");
    await page.getByLabel("E-mail").fill(`instr${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`);
    await page.getByLabel("Password").fill("a long passphrase 1");
    await page.getByRole("button", { name: "Create account" }).click();
    await enrollAfterSignUp(page, "mvc");

    await page.goto(`/test/${UNIT}`);
    const started = page.waitForResponse((r) => r.url().endsWith("/api/unit-tests") && r.request().method() === "POST");
    await page.getByRole("button", { name: "Start the test" }).click();
    const body = (await (await started).json()) as { questions: { taskHtml?: string }[] };
    expect(body.questions).toHaveLength(10);
    for (const q of body.questions) expect((q.taskHtml ?? "").length).toBeGreaterThan(5);
    // and each question shows it above its statement
    await expect(page.locator("li p.font-semibold")).toHaveCount(10);
  });
});
