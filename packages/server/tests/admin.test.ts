import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { eq } from "drizzle-orm";
import { schema, type DbHandle } from "@allmaths/db";
import { openTestDb } from "@allmaths/db/testing";
import {
  adminResetPassword,
  authenticate,
  completePasswordReset,
  createPasswordReset,
  createSession,
  getAdminStats,
  listUsers,
  registerStudent,
  setUserRole,
  setUserSuspended,
  upsertUserWithRole,
  validateSession,
  RESET_MAX_ATTEMPTS,
} from "../src";

let h: DbHandle;
let adminId: string;
let studentId: string;
beforeAll(async () => {
  h = await openTestDb();
  adminId = await upsertUserWithRole(h.db, { email: "boss@example.com", name: "Boss", password: "boss password 12", role: "admin" });
  const s = await registerStudent(h.db, { email: "learner@example.com", name: "Learner One", password: "learner password 1" });
  studentId = s.id;
});
afterAll(async () => {
  await h.close();
});

const signIn = (email: string, password: string) => authenticate(h.db, { email, password });

describe("forgot password", () => {
  it("gives nothing for an unknown e-mail, so the form cannot reveal who is registered", async () => {
    expect(await createPasswordReset(h.db, "nobody@example.com")).toBeNull();
    expect(await createPasswordReset(h.db, "not an e-mail")).toBeNull();
  });

  it("a valid code sets the new password, ends the sessions and works only once", async () => {
    const { token } = await createSession(h.db, studentId);
    const r = await createPasswordReset(h.db, "Learner@Example.com");
    expect(r?.code).toMatch(/^\d{6}$/);
    await completePasswordReset(h.db, { email: "learner@example.com", code: r!.code, password: "brand new password 9" });
    await expect(signIn("learner@example.com", "learner password 1")).rejects.toMatchObject({ code: "invalid_credentials" });
    expect((await signIn("learner@example.com", "brand new password 9")).id).toBe(studentId);
    expect(await validateSession(h.db, token)).toBeNull();
    await expect(completePasswordReset(h.db, { email: "learner@example.com", code: r!.code, password: "another password 10" })).rejects.toMatchObject({ code: "invalid_code" });
  });

  it("the code expires after 10 minutes", async () => {
    const t0 = new Date("2030-01-01T10:00:00Z");
    const r = await createPasswordReset(h.db, "learner@example.com", t0);
    const late = new Date(t0.getTime() + 10 * 60_000 + 1000);
    await expect(completePasswordReset(h.db, { email: "learner@example.com", code: r!.code, password: "late password 123" }, late)).rejects.toMatchObject({ code: "invalid_code" });
    const early = new Date(t0.getTime() + 9 * 60_000);
    await completePasswordReset(h.db, { email: "learner@example.com", code: r!.code, password: "early password 123" }, early);
  });

  it("a wrong code is refused and, after five tries, even the right code is refused", async () => {
    const r = await createPasswordReset(h.db, "learner@example.com");
    const wrong = r!.code === "000000" ? "111111" : "000000";
    for (let i = 0; i < RESET_MAX_ATTEMPTS; i++) {
      await expect(completePasswordReset(h.db, { email: "learner@example.com", code: wrong, password: "never used pass 1" })).rejects.toMatchObject({ code: "invalid_code" });
    }
    await expect(completePasswordReset(h.db, { email: "learner@example.com", code: r!.code, password: "never used pass 1" })).rejects.toMatchObject({ code: "invalid_code" });
  });

  it("a new code replaces the old one, and a suspended account gets none", async () => {
    const first = await createPasswordReset(h.db, "learner@example.com");
    const second = await createPasswordReset(h.db, "learner@example.com");
    if (first!.code !== second!.code) {
      await expect(completePasswordReset(h.db, { email: "learner@example.com", code: first!.code, password: "replaced code pass 1" })).rejects.toMatchObject({ code: "invalid_code" });
    }
    await setUserSuspended(h.db, adminId, studentId, true);
    expect(await createPasswordReset(h.db, "learner@example.com")).toBeNull();
    await setUserSuspended(h.db, adminId, studentId, false);
  });

  it("refuses a weak new password", async () => {
    const r = await createPasswordReset(h.db, "learner@example.com");
    await expect(completePasswordReset(h.db, { email: "learner@example.com", code: r!.code, password: "password123" })).rejects.toMatchObject({ code: "weak_password" });
  });
});

describe("administrator tools", () => {
  it("resets a password to a temporary one, ends the sessions and writes the audit log", async () => {
    const { token } = await createSession(h.db, studentId);
    const temporary = await adminResetPassword(h.db, adminId, studentId);
    expect(temporary.length).toBeGreaterThanOrEqual(12);
    expect((await signIn("learner@example.com", temporary)).id).toBe(studentId);
    expect(await validateSession(h.db, token)).toBeNull();
    const log = await h.db.select().from(schema.auditLog).where(eq(schema.auditLog.target, studentId));
    expect(log.some((l) => l.action === "user.password_reset" && l.actorId === adminId)).toBe(true);
  });

  it("suspends and restores an account; a suspended user cannot sign in", async () => {
    await setUserSuspended(h.db, adminId, studentId, true);
    await expect(signIn("learner@example.com", "x")).rejects.toMatchObject({ code: "invalid_credentials" });
    const [row] = (await listUsers(h.db, { q: "learner" })).filter((u) => u.id === studentId);
    expect(row?.suspended).toBe(true);
    await setUserSuspended(h.db, adminId, studentId, false);
    expect((await listUsers(h.db, { q: "learner" })).find((u) => u.id === studentId)?.suspended).toBe(false);
  });

  it("an administrator cannot suspend or demote themselves; roles can be changed for others", async () => {
    await expect(setUserSuspended(h.db, adminId, adminId, true)).rejects.toMatchObject({ code: "self_action" });
    await expect(setUserRole(h.db, adminId, adminId, "student")).rejects.toMatchObject({ code: "self_action" });
    await setUserRole(h.db, adminId, studentId, "instructor");
    expect((await listUsers(h.db, { q: "learner" }))[0]?.role).toBe("instructor");
    await setUserRole(h.db, adminId, studentId, "student");
  });

  it("an unknown user is not found", async () => {
    await expect(adminResetPassword(h.db, adminId, "00000000-0000-4000-8000-000000000000")).rejects.toMatchObject({ code: "not_found" });
  });

  it("searches by name or e-mail and treats % and _ as plain characters", async () => {
    expect((await listUsers(h.db, { q: "Learner One" })).map((u) => u.email)).toEqual(["learner@example.com"]);
    expect(await listUsers(h.db, { q: "%" })).toEqual([]);
    expect((await listUsers(h.db)).length).toBeGreaterThanOrEqual(2);
  });

  it("counts users by role, recent signups and activity", async () => {
    await createSession(h.db, studentId);
    const s = await getAdminStats(h.db);
    expect(s.totalUsers).toBe(2);
    expect(s.byRole.admin).toBe(1);
    expect(s.byRole.student).toBe(1);
    expect(s.newLast7Days).toBe(2);
    expect(s.activeLast7Days).toBeGreaterThanOrEqual(1);
    expect(s.suspended).toBe(0);
    expect(s.courses).toEqual([]);
  });

  it("counts learners who entered and completed a course", async () => {
    await h.db.insert(schema.courses).values({ id: "c1", slug: "c1", title: "Course One", order: 1 });
    await h.db.insert(schema.modules).values({ id: "c1-m1", courseId: "c1", order: 1, title: "M" });
    await h.db.insert(schema.units).values({ id: "c1-m1-u1", moduleId: "c1-m1", order: 1, title: "U" });
    await h.db.insert(schema.lessons).values({ id: "c1-m1-u1-l1", unitId: "c1-m1-u1", order: 1, title: "L", estMinutes: 5 });
    await h.db.insert(schema.sections).values({ id: "c1-m1-u1-l1:s1", lessonId: "c1-m1-u1-l1", order: 1, type: "text", contentJson: {} });
    await h.db.insert(schema.sectionProgress).values({ userId: studentId, sectionId: "c1-m1-u1-l1:s1", lessonId: "c1-m1-u1-l1" });
    let c = (await getAdminStats(h.db)).courses[0];
    expect(c).toMatchObject({ courseId: "c1", entered: 1, completed: 0 });
    await h.db.insert(schema.progress).values({ userId: studentId, objectType: "course", objectId: "c1", num: 1n, den: 1n, percent: 100 });
    c = (await getAdminStats(h.db)).courses[0];
    expect(c).toMatchObject({ entered: 1, completed: 1 });
  });
});
