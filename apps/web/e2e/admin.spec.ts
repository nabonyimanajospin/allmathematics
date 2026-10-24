import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Browser, type Page } from "@playwright/test";
import { enrollAfterSignUp } from "./helpers";

// The e-mail listed in ADMIN_EMAILS of the test server (playwright.config.ts): signing up with it makes an administrator.
const ADMIN_EMAIL = "e2e-admin@example.com";
const PASSWORD = "a long passphrase 1";
const unique = () => `ad${Date.now()}${Math.floor(Math.random() * 1000)}@example.com`;

async function signUp(page: Page, email: string, name: string, course: "geo" | "mvc" | "stat" = "geo"): Promise<void> {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill(name);
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: "Create account" }).click();
  await enrollAfterSignUp(page, course);
}

/** The administrator account of the test server: created by the first sign-up (a later one gets "taken", which is fine), then signed in. */
async function adminPage(browser: Browser, baseURL: string | undefined): Promise<Page> {
  const ctx = await browser.newContext({ ...(baseURL ? { baseURL } : {}) });
  const page = await ctx.newPage();
  const created = await page.request.post("/api/auth/signup", { data: { name: "Test Admin", email: ADMIN_EMAIL, password: PASSWORD }, headers: { origin: baseURL ?? "" } });
  if (created.status() !== 201) {
    // the account exists already (an earlier test made it): sign in with the form
    await page.goto("/signin");
    await page.getByLabel("E-mail").fill(ADMIN_EMAIL);
    await page.getByLabel("Password").fill(PASSWORD);
    await page.getByRole("button", { name: "Sign in" }).click();
    await page.waitForURL(/\/(dashboard|courses)/);
  }
  return page;
}

test.describe("feedback, announcements and the administration", () => {
  // the first visit of each administration page compiles it, which is slow on a cold server
  test.describe.configure({ timeout: 300_000 });

  test("a learner sends feedback; the administrator reads, resolves and deletes it", async ({ page, browser, baseURL }) => {
    const email = unique();
    await signUp(page, email, "Feedback Giver");
    await page.goto("/dashboard");
    await page.getByRole("link", { name: "Feedback" }).click();
    await expect(page.getByRole("heading", { name: "Send feedback", level: 1 })).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
    await page.getByLabel("What is it about?").selectOption("content");
    await page.getByLabel("Your message").fill("The answer of exercise 3 in the counting lesson looks wrong to me.");
    await page.getByRole("button", { name: "Send", exact: true }).click();
    await expect(page.getByRole("status")).toContainText("Thank you");

    const admin = await adminPage(browser, baseURL);
    await admin.goto("/admin/feedback");
    await expect(admin.getByRole("heading", { name: "Feedback from learners", level: 1 })).toBeVisible();
    const card = admin.locator("li", { hasText: "The answer of exercise 3 in the counting lesson looks wrong" }).first();
    await expect(card).toBeVisible();
    await expect(card).toContainText("Feedback Giver");
    await expect(card).toContainText(email);
    await card.getByLabel(/Private note/).fill("Checked: it is correct.");
    await card.getByRole("button", { name: "Mark as resolved" }).click();
    await expect(card).toContainText("Resolved"); // the page refreshes after the server saved the decision
    await admin.goto("/admin/feedback?status=resolved");
    const resolved = admin.locator("li", { hasText: "The answer of exercise 3 in the counting lesson looks wrong" }).first();
    await expect(resolved).toContainText("Resolved");
    await expect(resolved.getByLabel(/Private note/)).toHaveValue("Checked: it is correct.");
    admin.once("dialog", (d) => void d.accept());
    await resolved.getByRole("button", { name: "Delete" }).click();
    await expect(admin.locator("li", { hasText: "The answer of exercise 3 in the counting lesson looks wrong" })).toHaveCount(0);

    // the audit log recorded what the administrator did
    await admin.goto("/admin/audit");
    await expect(admin.getByText("feedback.resolved").first()).toBeVisible();
    await expect(admin.getByText("feedback.delete").first()).toBeVisible();
    await admin.context().close();
  });

  test("an announcement shows to learners until it is hidden", async ({ page, browser, baseURL }) => {
    const admin = await adminPage(browser, baseURL);
    await admin.goto("/admin/announcements");
    const text = `The test of Unit 1 is on Friday ${Date.now()}.`;
    await admin.getByLabel("Message").fill(text);
    await admin.getByRole("button", { name: "Publish" }).click();
    await expect(admin.getByRole("main").getByText(text).first()).toBeVisible();

    await signUp(page, unique(), "Announcement Reader");
    await expect(page.getByRole("region", { name: "Announcements" })).toContainText(text);

    const row = admin.getByRole("main").locator("li", { hasText: text }).first();
    await row.getByRole("button", { name: "Hide" }).click();
    await expect(row).toContainText("Hidden");
    await page.reload();
    await expect(page.getByText(text)).toHaveCount(0);
    admin.once("dialog", (d) => void d.accept());
    await row.getByRole("button", { name: "Delete" }).click();
    await expect(admin.getByRole("main").getByText(text)).toHaveCount(0);
    await admin.context().close();
  });

  test("only an administrator reaches the administration, and the CSV of accounts is protected", async ({ page, browser, baseURL }) => {
    await signUp(page, unique(), "Plain Learner");
    expect((await page.request.get("/admin/feedback")).status()).toBe(404);
    expect((await page.request.get("/admin/audit")).status()).toBe(404);
    expect((await page.request.get("/api/admin/users/export")).status()).toBe(403);
    expect((await page.request.post("/api/feedback", { data: { category: "idea", message: "x" }, headers: { origin: new URL(page.url()).origin } })).status()).toBe(400);

    const admin = await adminPage(browser, baseURL);
    const csv = await admin.request.get("/api/admin/users/export");
    expect(csv.status()).toBe(200);
    expect(csv.headers()["content-type"]).toContain("text/csv");
    expect(await csv.text()).toContain("name,email,role,created,status");
    await admin.goto("/admin");
    const menu = admin.getByRole("navigation", { name: "Administration" });
    await expect(menu.getByRole("link", { name: "Feedback" })).toBeVisible();
    await expect(menu.getByRole("link", { name: "Announcements" })).toBeVisible();
    await expect(menu.getByRole("link", { name: "Audit log" })).toBeVisible();
    const a11y = await new AxeBuilder({ page: admin }).analyze();
    expect(a11y.violations).toEqual([]);
    await admin.context().close();
  });

  test("a signed-out visitor is sent to sign in for the feedback page", async ({ page }) => {
    await page.goto("/feedback");
    await expect(page).toHaveURL(/\/signin/);
  });
});
