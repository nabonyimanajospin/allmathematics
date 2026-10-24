import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { randomUUID } from "node:crypto";
import { schema } from "@allmaths/db";
import {
  createAnnouncement,
  deleteAnnouncement,
  deleteFeedback,
  feedbackCounts,
  listAnnouncements,
  listAudit,
  listFeedback,
  setAnnouncementActive,
  setFeedbackStatus,
  submitFeedback,
  usersCsv,
} from "../src";
import { makeFixture, type Fixture } from "./helpers";

let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
});
afterAll(async () => {
  await f.h.close();
});

describe("feedback from learners", () => {
  it("is stored with the author and the page, and the administrator can read and resolve it", async () => {
    const id = await submitFeedback(f.h.db, f.userId, { category: "content", message: "  The answer of exercise 3 looks wrong.  ", page: "/learn/geo-m01-u01-l01" });
    const [admin] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "Boss", role: "admin" }).returning();
    let rows = await listFeedback(f.h.db);
    const row = rows.find((r) => r.id === id)!;
    expect(row).toMatchObject({ category: "content", message: "The answer of exercise 3 looks wrong.", page: "/learn/geo-m01-u01-l01", status: "new" });
    expect(row.userEmail).toBeTruthy();
    expect((await feedbackCounts(f.h.db)).new).toBeGreaterThanOrEqual(1);

    await setFeedbackStatus(f.h.db, admin!.id, id, "resolved", "Fixed in the next release");
    rows = await listFeedback(f.h.db, { status: "resolved" });
    expect(rows.find((r) => r.id === id)).toMatchObject({ status: "resolved", adminNote: "Fixed in the next release" });
    expect((await listFeedback(f.h.db, { status: "new" })).some((r) => r.id === id)).toBe(false);
    const audit = await listAudit(f.h.db);
    expect(audit.some((a) => a.action === "feedback.resolved" && a.target === id && a.actorEmail !== null)).toBe(true);

    await deleteFeedback(f.h.db, admin!.id, id);
    expect((await listFeedback(f.h.db)).some((r) => r.id === id)).toBe(false);
    await expect(deleteFeedback(f.h.db, admin!.id, id)).rejects.toMatchObject({ code: "not_found" });
  });

  it("refuses an unknown category, a message that is too short or too long, and keeps only a safe page path", async () => {
    await expect(submitFeedback(f.h.db, f.userId, { category: "spam", message: "hello there" })).rejects.toMatchObject({ code: "invalid_category" });
    await expect(submitFeedback(f.h.db, f.userId, { category: "idea", message: "hi" })).rejects.toMatchObject({ code: "message_too_short" });
    await expect(submitFeedback(f.h.db, f.userId, { category: "idea", message: "x".repeat(2001) })).rejects.toMatchObject({ code: "message_too_long" });
    const id = await submitFeedback(f.h.db, f.userId, { category: "idea", message: "Please add more examples", page: "https://evil.example/x" });
    expect((await listFeedback(f.h.db)).find((r) => r.id === id)!.page).toBeNull();
    await expect(setFeedbackStatus(f.h.db, f.userId, id, "banana")).rejects.toMatchObject({ code: "invalid_status" });
  });
});

describe("announcements", () => {
  it("are shown while active, can be hidden and deleted, and are audited", async () => {
    const [admin] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "Boss", role: "admin" }).returning();
    const id = await createAnnouncement(f.h.db, admin!.id, "The test of Unit 1 is on Friday.");
    expect((await listAnnouncements(f.h.db, { onlyActive: true })).some((a) => a.id === id)).toBe(true);
    await setAnnouncementActive(f.h.db, admin!.id, id, false);
    expect((await listAnnouncements(f.h.db, { onlyActive: true })).some((a) => a.id === id)).toBe(false);
    expect((await listAnnouncements(f.h.db)).some((a) => a.id === id)).toBe(true);
    await deleteAnnouncement(f.h.db, admin!.id, id);
    expect((await listAnnouncements(f.h.db)).some((a) => a.id === id)).toBe(false);
    await expect(createAnnouncement(f.h.db, admin!.id, "no")).rejects.toMatchObject({ code: "invalid_message" });
    const actions = (await listAudit(f.h.db)).filter((a) => a.target === id).map((a) => a.action);
    expect(actions).toEqual(expect.arrayContaining(["announcement.create", "announcement.hide", "announcement.delete"]));
  });
});

describe("the list of accounts as CSV", () => {
  it("has a header, quotes every cell and defuses spreadsheet formulas", async () => {
    await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: '=HYPERLINK("http://evil")', role: "student" });
    const csv = await usersCsv(f.h.db);
    expect(csv.startsWith("name,email,role,created,status\r\n")).toBe(true);
    expect(csv).toContain("\"'=HYPERLINK(\"\"http://evil\"\")\"");
    for (const l of csv.split("\r\n")) if (l !== "" && !l.startsWith("name,")) expect(l.startsWith('"')).toBe(true);
  });
});
