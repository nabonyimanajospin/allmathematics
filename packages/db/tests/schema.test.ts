import { eq, sql } from "drizzle-orm";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { schema, type DbHandle } from "../src";
import { openTestDb } from "../src/testing";

let h: DbHandle;
beforeAll(async () => {
  h = await openTestDb();
});
afterAll(async () => {
  await h.close();
});

describe("migrations", () => {
  it("create every table of spec section 11", async () => {
    const rows = (await h.db.execute(
      sql`select table_name from information_schema.tables where table_schema = 'public'`,
    )) as unknown as { rows: { table_name: string }[] };
    const names = new Set(rows.rows.map((r) => r.table_name));
    for (const t of [
      "users", "courses", "modules", "units", "lessons", "sections", "skills", "problem_templates",
      "template_skills", "problem_instances", "assessments", "attempts", "responses", "events", "progress",
      "mastery", "enrollments", "subscriptions", "payments", "classes", "class_members", "assignments",
      "forum_threads", "forum_posts", "notes", "bookmarks", "certificates", "audit_log", "sessions",
      "section_progress",
    ]) {
      expect(names.has(t), `table ${t}`).toBe(true);
    }
  });
});

describe("users", () => {
  it("emails are unique case-insensitively", async () => {
    await h.db.insert(schema.users).values({ email: "Ada@Example.com", name: "Ada" });
    await expect(h.db.insert(schema.users).values({ email: "ada@example.com", name: "Ada 2" })).rejects.toThrow();
  });

  it("defaults to the student role and cascades sessions on delete", async () => {
    const [u] = await h.db.insert(schema.users).values({ email: "s@example.com", name: "S" }).returning();
    expect(u?.role).toBe("student");
    await h.db.insert(schema.sessions).values({
      userId: u!.id,
      tokenHash: "hash-1",
      expiresAt: new Date(Date.now() + 1000),
    });
    await h.db.delete(schema.users).where(eq(schema.users.id, u!.id));
    const left = await h.db.select().from(schema.sessions).where(eq(schema.sessions.tokenHash, "hash-1"));
    expect(left).toHaveLength(0);
  });

  it("rejects an unknown role", async () => {
    await expect(
      h.db.execute(sql`insert into users (email, name, role) values ('x@example.com','X','superuser')`),
    ).rejects.toThrow();
  });
});

describe("events", () => {
  it("is idempotent on the client-generated id", async () => {
    const [u] = await h.db.insert(schema.users).values({ email: "e@example.com", name: "E" }).returning();
    const row = {
      id: "6f1c3b0e-5c1b-4a43-9d58-0d3f0b0f7a11",
      userId: u!.id,
      verb: "viewed" as const,
      objectType: "section",
      objectId: "x",
    };
    await h.db.insert(schema.events).values(row).onConflictDoNothing();
    await h.db.insert(schema.events).values(row).onConflictDoNothing();
    const all = await h.db.select().from(schema.events).where(eq(schema.events.userId, u!.id));
    expect(all).toHaveLength(1);
  });
});

describe("progress", () => {
  it("stores exact fractions with bigint precision", async () => {
    const [u] = await h.db.insert(schema.users).values({ email: "p@example.com", name: "P" }).returning();
    await h.db.insert(schema.progress).values({
      userId: u!.id, objectType: "lesson", objectId: "l", num: 12345678901234567n, den: 98765432109876543n, percent: 12,
    });
    const [r] = await h.db.select().from(schema.progress).where(eq(schema.progress.userId, u!.id));
    expect(r?.num).toBe(12345678901234567n);
    expect(r?.den).toBe(98765432109876543n);
  });
});
