import { expect, test } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

// The first quick check of this lesson: "Find the radius of the circle ..." with two hints.
const LESSON = "geo-m02-u03-l01";

test.describe("hints", () => {
  test("a double click on the hint button shows one hint, not the same hint twice", async ({ page }) => {
    await page.goto("/signup");
    await page.getByLabel("Full name").fill("Hint Tester");
    await page.getByLabel("E-mail").fill(`hint${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`);
    await page.getByLabel("Password").fill("a long passphrase 1");
    await page.getByRole("button", { name: "Create account" }).click();
    await enrollAfterSignUp(page, "geo");
    await page.goto(`/learn/${LESSON}`);
    const hintButton = page.getByRole("button", { name: /Show a hint/ }).first();
    await hintButton.scrollIntoViewIfNeeded();
    await hintButton.dblclick();
    const shown = page.locator("ol > li", { hasText: "Complete the squares in" });
    await expect(shown).toHaveCount(1);
    // the second hint comes only after the first, and it is a different one
    await page.getByRole("button", { name: /Show a hint/ }).first().click();
    await expect(page.locator("ol > li", { hasText: "The right side of" })).toHaveCount(1);
    await expect(shown).toHaveCount(1);
  });
});
