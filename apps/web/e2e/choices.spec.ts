import { expect, test } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

// The first quick check of this lesson: "Which surface is z = x^2 - y^2?", three options, the second one is right.
const LESSON = "geo-m03-u04-l01";

test.describe("a multiple-choice question that was answered", () => {
  test("shows the chosen option as selected when the learner comes back, instead of an empty list marked Correct", async ({ page }) => {
    await page.goto("/signup");
    await page.getByLabel("Full name").fill("Choice Tester");
    await page.getByLabel("E-mail").fill(`choice${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`);
    await page.getByLabel("Password").fill("a long passphrase 1");
    await page.getByRole("button", { name: "Create account" }).click();
    await enrollAfterSignUp(page, "geo");

    await page.goto(`/learn/${LESSON}`);
    // it is the first quick check of the lesson, so it is the only question with options on the page
    const question = page;
    const options = page.getByRole("radio");
    await expect(options).toHaveCount(3);
    await options.nth(0).check(); // a wrong option first
    await question.getByRole("button", { name: "Check" }).click();
    await expect(question.getByText("Not correct yet")).toBeVisible();
    await options.nth(1).check();
    await question.getByRole("button", { name: "Check" }).click();
    await expect(question.getByText("Correct.")).toBeVisible();

    await page.reload();
    await expect(page.getByText("Correct.")).toBeVisible();
    const radios = page.getByRole("radio");
    await expect(radios.nth(1)).toBeChecked();
    await expect(radios.nth(0)).not.toBeChecked();
    await expect(radios.nth(1)).toBeDisabled(); // it stays answered: the choice cannot be changed after a correct answer
  });
});
