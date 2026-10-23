import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { randomUUID } from "node:crypto";
import { schema } from "@allmaths/db";
import { grantPremium, hasPremium, recordSolve, revokePremium, solverAccess, upsertUserWithRole } from "../src";
import { makeFixture, type Fixture } from "./helpers";

const NOW = new Date("2026-10-23T10:00:00Z");
let f: Fixture;
let adminId: string;
beforeAll(async () => {
  f = await makeFixture();
  adminId = await upsertUserWithRole(f.h.db, { email: "root@example.com", name: "Root", password: "root password 123", role: "admin" });
});
afterAll(async () => {
  await f.h.close();
});

describe("the solver plans", () => {
  it("the free plan has a daily limit that frees up after 24 hours", async () => {
    expect(await solverAccess(f.h.db, f.userId, 3, NOW)).toEqual({ premium: false, used: 0, limit: 3, remaining: 3 });
    for (let i = 0; i < 3; i++) await recordSolve(f.h.db, f.userId, "derivative", new Date(NOW.getTime() + i * 1000));
    expect(await solverAccess(f.h.db, f.userId, 3, new Date(NOW.getTime() + 10_000))).toMatchObject({ used: 3, remaining: 0 });
    // 25 hours later the three solves are outside the window
    expect(await solverAccess(f.h.db, f.userId, 3, new Date(NOW.getTime() + 25 * 3_600_000))).toMatchObject({ used: 0, remaining: 3 });
  });

  it("Premium has no limit, ends when it expires and can be revoked", async () => {
    const [u] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "Payer" }).returning();
    const id = u!.id;
    const end = await grantPremium(f.h.db, adminId, id, 30, NOW);
    expect(end.getTime() - NOW.getTime()).toBe(30 * 86_400_000);
    for (let i = 0; i < 8; i++) await recordSolve(f.h.db, id, "integral", NOW);
    expect(await solverAccess(f.h.db, id, 3, NOW)).toEqual({ premium: true, used: 8, limit: null, remaining: null });
    expect(await hasPremium(f.h.db, id, new Date(end.getTime() + 1000))).toBe(false); // expired
    await revokePremium(f.h.db, adminId, id);
    expect(await hasPremium(f.h.db, id, NOW)).toBe(false);
    const log = await f.h.db.select().from(schema.auditLog);
    expect(log.map((l) => l.action)).toEqual(expect.arrayContaining(["premium.grant", "premium.revoke"]));
  });

  it("refuses a nonsense duration and an unknown user", async () => {
    await expect(grantPremium(f.h.db, adminId, f.userId, 0)).rejects.toMatchObject({ code: "invalid_days" });
    await expect(grantPremium(f.h.db, adminId, randomUUID(), 30)).rejects.toMatchObject({ code: "not_found" });
  });
});
