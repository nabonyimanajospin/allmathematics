import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { schema, type DbHandle } from "@allmaths/db";
import { openTestDb } from "@allmaths/db/testing";
import { eq } from "drizzle-orm";
import {
  authenticate,
  can,
  createMemoryRateLimiter,
  createSession,
  deleteSession,
  hashPassword,
  hashToken,
  registerStudent,
  validateSession,
  verifyPassword,
  upsertUserWithRole,
} from "../src";

let h: DbHandle;
beforeAll(async () => {
  h = await openTestDb();
});
afterAll(async () => {
  await h.close();
});

const good = { email: "Ada@Example.com ", name: " Ada Lovelace ", password: "correct horse battery" };

describe("passwords", () => {
  it("hash and verify, with a different salt each time", async () => {
    const a = await hashPassword("secret-password-1");
    const b = await hashPassword("secret-password-1");
    expect(a).not.toBe(b);
    expect(await verifyPassword("secret-password-1", a)).toBe(true);
    expect(await verifyPassword("secret-password-2", a)).toBe(false);
    expect(a.startsWith("scrypt$")).toBe(true);
    expect(a).not.toContain("secret-password-1");
  });

  it("rejects malformed stored hashes instead of throwing", async () => {
    expect(await verifyPassword("x", "garbage")).toBe(false);
    expect(await verifyPassword("x", "scrypt$1$1$1$a$b")).toBe(false);
  });
});

describe("registration and sign-in", () => {
  it("registers a student with a normalized e-mail and never stores the password", async () => {
    const u = await registerStudent(h.db, good);
    expect(u.email).toBe("ada@example.com");
    expect(u.name).toBe("Ada Lovelace");
    expect(u.role).toBe("student");
    const [row] = await h.db.select().from(schema.users).where(eq(schema.users.id, u.id));
    expect(row?.passwordHash).toMatch(/^scrypt\$/);
    expect(JSON.stringify(row)).not.toContain(good.password);
  });

  it("refuses a duplicate e-mail in any letter case", async () => {
    await expect(registerStudent(h.db, { ...good, email: "ADA@example.com" })).rejects.toMatchObject({ code: "email_taken" });
  });

  it("validates input", async () => {
    await expect(registerStudent(h.db, { ...good, email: "nope" })).rejects.toMatchObject({ code: "invalid_input" });
    await expect(registerStudent(h.db, { ...good, email: "b@example.com", password: "short" })).rejects.toMatchObject({ code: "invalid_input" });
    await expect(registerStudent(h.db, { ...good, email: "c@example.com", name: "  " })).rejects.toMatchObject({ code: "invalid_input" });
    await expect(registerStudent(h.db, { ...good, email: "d@example.com", password: "password123" })).rejects.toMatchObject({ code: "weak_password" });
  });

  it("a user cannot choose their own role", async () => {
    const u = await registerStudent(h.db, { ...good, email: "evil@example.com", role: "admin" });
    expect(u.role).toBe("student");
  });

  it("signs in with the right password only; the error never says which part was wrong", async () => {
    const u = await authenticate(h.db, { email: "ADA@example.com", password: good.password });
    expect(u.name).toBe("Ada Lovelace");
    const wrongPassword = await authenticate(h.db, { email: "ada@example.com", password: "wrong wrong wrong" }).catch((e) => e);
    const unknownEmail = await authenticate(h.db, { email: "nobody@example.com", password: "wrong wrong wrong" }).catch((e) => e);
    expect(wrongPassword).toMatchObject({ code: "invalid_credentials", status: 401 });
    expect(unknownEmail.message).toBe(wrongPassword.message);
  });

  it("suspended accounts cannot sign in", async () => {
    const u = await registerStudent(h.db, { ...good, email: "sus@example.com" });
    await h.db.update(schema.users).set({ suspendedAt: new Date() }).where(eq(schema.users.id, u.id));
    await expect(authenticate(h.db, { email: "sus@example.com", password: good.password })).rejects.toMatchObject({ code: "invalid_credentials" });
  });
});

describe("sessions", () => {
  it("stores only a hash of the token and validates it", async () => {
    const u = await authenticate(h.db, { email: "ada@example.com", password: good.password });
    const { token } = await createSession(h.db, u.id);
    const stored = await h.db.select().from(schema.sessions).where(eq(schema.sessions.userId, u.id));
    expect(stored.some((s) => s.tokenHash === hashToken(token))).toBe(true);
    expect(JSON.stringify(stored)).not.toContain(token);
    expect((await validateSession(h.db, token))?.email).toBe("ada@example.com");
  });

  it("expires, can be deleted, and rejects malformed tokens", async () => {
    const u = await authenticate(h.db, { email: "ada@example.com", password: good.password });
    const t0 = new Date("2026-01-01T00:00:00Z");
    const { token } = await createSession(h.db, u.id, t0);
    expect(await validateSession(h.db, token, new Date(t0.getTime() + 29 * 86400_000))).not.toBeNull();
    // the check above renewed the session (sliding window), so test expiry on a session never used since
    const idle = (await createSession(h.db, u.id, t0)).token;
    expect(await validateSession(h.db, idle, new Date(t0.getTime() + 31 * 86400_000))).toBeNull();
    const fresh = (await createSession(h.db, u.id)).token;
    await deleteSession(h.db, fresh);
    expect(await validateSession(h.db, fresh)).toBeNull();
    expect(await validateSession(h.db, "short")).toBeNull();
    expect(await validateSession(h.db, "' OR 1=1 --".padEnd(44, "x"))).toBeNull();
  });

  it("a session dies when the user is suspended", async () => {
    const u = await registerStudent(h.db, { ...good, email: "later@example.com" });
    const { token } = await createSession(h.db, u.id);
    await h.db.update(schema.users).set({ suspendedAt: new Date() }).where(eq(schema.users.id, u.id));
    expect(await validateSession(h.db, token)).toBeNull();
  });
});

describe("roles and permissions", () => {
  it("only staff can do staff things", () => {
    expect(can("student", "class:manage")).toBe(false);
    expect(can("student", "users:manage")).toBe(false);
    expect(can("instructor", "class:manage")).toBe(true);
    expect(can("instructor", "users:manage")).toBe(false);
    expect(can("admin", "users:manage")).toBe(true);
    expect(can("admin", "resources:manage")).toBe(true);
    for (const role of ["student", "instructor", "content_author", "reviewer"] as const) expect(can(role, "resources:manage")).toBe(false);
    expect(can("reviewer", "content:review")).toBe(true);
    expect(can("content_author", "content:review")).toBe(false);
  });

  it("seed helper creates privileged users", async () => {
    const id = await upsertUserWithRole(h.db, { email: "teacher@example.com", name: "T", password: "teacher password 1", role: "instructor" });
    const again = await upsertUserWithRole(h.db, { email: "TEACHER@example.com", name: "T2", password: "teacher password 1", role: "admin" });
    expect(again).toBe(id);
    const u = await authenticate(h.db, { email: "teacher@example.com", password: "teacher password 1" });
    expect(u.role).toBe("admin");
  });
});

describe("rate limiter", () => {
  it("blocks after the limit and recovers after the window", () => {
    const rl = createMemoryRateLimiter(3, 1000);
    expect(rl.hit("ip", 0).allowed).toBe(true);
    expect(rl.hit("ip", 10).allowed).toBe(true);
    expect(rl.hit("ip", 20).allowed).toBe(true);
    const blocked = rl.hit("ip", 30);
    expect(blocked.allowed).toBe(false);
    expect(blocked.retryAfterMs).toBe(970);
    expect(rl.hit("other", 30).allowed).toBe(true);
    expect(rl.hit("ip", 1001).allowed).toBe(true);
  });
});
