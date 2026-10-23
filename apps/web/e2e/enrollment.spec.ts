import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { enrollAfterSignUp, switchCourse } from "./helpers";

const unique = () => `enrol${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function createAccount(page: Page): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Course Chooser");
  await page.getByLabel("E-mail").fill(unique());
  await page.getByLabel("Password").fill("a long passphrase 1");
  await page.getByRole("button", { name: "Create account" }).click();
}

test.describe("one course at a time", () => {
  test("a new learner must choose a course; the other courses stay closed until they switch", async ({ page }) => {
    await createAccount(page);
    await page.waitForURL("**/courses");
    // before enrolling, a lesson sends the learner to the chooser
    await page.goto("/learn/geo-m01-u01-l01");
    await page.waitForURL("**/courses");
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    await page.getByRole("button", { name: "Enroll in this course" }).first().click();
    await page.waitForURL("**/dashboard");
    await expect(page.getByRole("heading", { name: "Geometry", level: 2 })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Multivariable Calculus and Differential Equations", level: 2 })).toHaveCount(0);

    // a lesson of another course is closed
    await page.goto("/learn/mvc-m01-u01-l01");
    await page.waitForURL("**/courses");

    // switching opens it and keeps the first one's progress
    await switchCourse(page, "mvc");
    await expect(page.getByRole("heading", { name: "Multivariable Calculus and Differential Equations", level: 2 })).toBeVisible();
    await page.goto("/learn/mvc-m01-u01-l01");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await page.goto("/learn/geo-m01-u01-l01");
    await page.waitForURL("**/courses");
  });

  test("the lesson sheet is printable, has all the exercises and shows no answers", async ({ page }) => {
    await createAccount(page);
    await enrollAfterSignUp(page, "geo");
    await page.goto("/learn/geo-m01-u01-l01");
    await page.getByRole("link", { name: "Printable lesson sheet" }).click();
    await page.waitForURL("**/learn/geo-m01-u01-l01/sheet");
    await expect(page.getByRole("heading", { name: "Exercises", level: 2 })).toBeVisible();
    await expect(page.getByRole("button", { name: "Print this sheet" })).toBeVisible();
    await expect(page.getByText("15.", { exact: true })).toBeVisible();
    // the sheet's own HTML (not the page left behind by client-side navigation) carries no answer data at all
    const html = await (await page.request.get("/learn/geo-m01-u01-l01/sheet")).text();
    expect(html).not.toContain("correctIndex");
    expect(html).not.toContain("answerType");
    await page.getByRole("link", { name: /Back to the lesson/ }).click();
    await page.waitForURL("**/learn/geo-m01-u01-l01");
  });
});
