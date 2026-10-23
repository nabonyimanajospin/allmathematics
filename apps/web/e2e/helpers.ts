import { expect, type Page } from "@playwright/test";

export const COURSE_TITLES = {
  geo: "Geometry",
  mvc: "Multivariable Calculus and Differential Equations",
  stat: "Probability and Statistics",
} as const;

/** After creating an account the learner chooses a course; this picks one and waits for the dashboard. */
export async function enrollAfterSignUp(page: Page, course: keyof typeof COURSE_TITLES): Promise<void> {
  await page.waitForURL("**/courses");
  await expect(page.getByRole("heading", { name: "Choose your course", level: 1 })).toBeVisible();
  const card = page.locator("div", { has: page.getByRole("heading", { name: COURSE_TITLES[course], level: 2, exact: true }) }).last();
  await card.getByRole("button", { name: "Enroll in this course" }).click();
  await page.waitForURL("**/dashboard");
}

/** Switch to another course from the dashboard (progress is kept). */
export async function switchCourse(page: Page, course: keyof typeof COURSE_TITLES): Promise<void> {
  await page.goto("/courses");
  page.once("dialog", (d) => void d.accept());
  const card = page.locator("div", { has: page.getByRole("heading", { name: COURSE_TITLES[course], level: 2, exact: true }) }).last();
  await card.getByRole("button", { name: "Switch to this course" }).click();
  await page.waitForURL("**/dashboard");
}
