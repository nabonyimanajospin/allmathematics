/** The minimum an administrator needs: platform numbers, finding a user, recovering or suspending an account. */

import { and, count, countDistinct, desc, eq, gt, gte, ilike, isNull, or, sql } from "drizzle-orm";
import { randomBytes } from "node:crypto";
import { ROLES, schema, type AppDb, type Role } from "@allmaths/db";
import { Errors, AppError } from "../errors";
import { hashPassword } from "../auth/password";
import { deleteAllSessions } from "../auth/users";

const DAY = 24 * 3600 * 1000;

export interface CourseStat {
  courseId: string;
  title: string;
  /** Learners who opened at least one section of the course. */
  entered: number;
  /** Learners at 100% of the course. */
  completed: number;
}

export interface AdminStats {
  totalUsers: number;
  byRole: Record<Role, number>;
  suspended: number;
  newLast7Days: number;
  activeLast7Days: number;
  courses: CourseStat[];
}

export async function getAdminStats(db: AppDb, now = new Date()): Promise<AdminStats> {
  const since = new Date(now.getTime() - 7 * DAY);
  const alive = isNull(schema.users.deletedAt);
  const roleRows = await db.select({ role: schema.users.role, n: count() }).from(schema.users).where(alive).groupBy(schema.users.role);
  const byRole = Object.fromEntries(ROLES.map((r) => [r, 0])) as Record<Role, number>;
  for (const r of roleRows) byRole[r.role] = r.n;
  const [suspended] = await db.select({ n: count() }).from(schema.users).where(and(alive, sql`${schema.users.suspendedAt} is not null`));
  const [fresh] = await db.select({ n: count() }).from(schema.users).where(and(alive, gte(schema.users.createdAt, since)));
  const [active] = await db
    .select({ n: countDistinct(schema.sessions.userId) })
    .from(schema.sessions)
    .innerJoin(schema.users, eq(schema.users.id, schema.sessions.userId))
    .where(and(alive, gte(schema.sessions.lastSeenAt, since)));

  const courses = await db.select({ id: schema.courses.id, title: schema.courses.title }).from(schema.courses).orderBy(schema.courses.order);
  const enteredRows = await db
    .select({ courseId: schema.modules.courseId, n: countDistinct(schema.sectionProgress.userId) })
    .from(schema.sectionProgress)
    .innerJoin(schema.lessons, eq(schema.lessons.id, schema.sectionProgress.lessonId))
    .innerJoin(schema.units, eq(schema.units.id, schema.lessons.unitId))
    .innerJoin(schema.modules, eq(schema.modules.id, schema.units.moduleId))
    .innerJoin(schema.users, eq(schema.users.id, schema.sectionProgress.userId))
    .where(alive)
    .groupBy(schema.modules.courseId);
  const doneRows = await db
    .select({ courseId: schema.progress.objectId, n: count() })
    .from(schema.progress)
    .innerJoin(schema.users, eq(schema.users.id, schema.progress.userId))
    .where(and(alive, eq(schema.progress.objectType, "course"), gte(schema.progress.percent, 100)))
    .groupBy(schema.progress.objectId);
  const entered = new Map(enteredRows.map((r) => [r.courseId, r.n]));
  const done = new Map(doneRows.map((r) => [r.courseId, r.n]));
  return {
    totalUsers: Object.values(byRole).reduce((a, b) => a + b, 0),
    byRole,
    suspended: suspended?.n ?? 0,
    newLast7Days: fresh?.n ?? 0,
    activeLast7Days: active?.n ?? 0,
    courses: courses.map((c) => ({ courseId: c.id, title: c.title, entered: entered.get(c.id) ?? 0, completed: done.get(c.id) ?? 0 })),
  };
}

export interface AdminUserRow {
  id: string;
  email: string;
  name: string;
  role: Role;
  suspended: boolean;
  premium: boolean;
  createdAt: Date;
  lastSeenAt: Date | null;
}

/** Newest accounts first; `q` matches part of the name or the e-mail. */
export async function listUsers(db: AppDb, opts: { q?: string; limit?: number } = {}): Promise<AdminUserRow[]> {
  const q = opts.q?.trim().slice(0, 100);
  const pattern = q ? `%${q.replace(/[\\%_]/g, (c) => `\\${c}`)}%` : null;
  const rows = await db
    .select({
      id: schema.users.id,
      email: schema.users.email,
      name: schema.users.name,
      role: schema.users.role,
      suspendedAt: schema.users.suspendedAt,
      createdAt: schema.users.createdAt,
      lastSeenAt: sql<Date | null>`(select max(${schema.sessions.lastSeenAt}) from ${schema.sessions} where ${schema.sessions.userId} = ${schema.users.id})`,
    })
    .from(schema.users)
    .where(and(isNull(schema.users.deletedAt), pattern ? or(ilike(schema.users.email, pattern), ilike(schema.users.name, pattern)) : undefined))
    .orderBy(desc(schema.users.createdAt))
    .limit(Math.min(opts.limit ?? 50, 200));
  const now = new Date();
  const premiumIds = new Set(
    (
      await db
        .select({ userId: schema.subscriptions.userId })
        .from(schema.subscriptions)
        .where(and(eq(schema.subscriptions.status, "active"), eq(schema.subscriptions.plan, "premium"), or(isNull(schema.subscriptions.currentPeriodEnd), gt(schema.subscriptions.currentPeriodEnd, now))))
    ).map((r) => r.userId),
  );
  return rows.map((r) => ({
    id: r.id,
    email: r.email,
    name: r.name,
    role: r.role,
    suspended: r.suspendedAt !== null,
    premium: premiumIds.has(r.id),
    createdAt: r.createdAt,
    lastSeenAt: r.lastSeenAt ? new Date(r.lastSeenAt) : null,
  }));
}

async function audit(db: AppDb, actorId: string, action: string, target: string): Promise<void> {
  await db.insert(schema.auditLog).values({ actorId, action, target });
}

async function targetUser(db: AppDb, id: string): Promise<{ id: string; email: string }> {
  const [u] = await db.select({ id: schema.users.id, email: schema.users.email }).from(schema.users).where(and(eq(schema.users.id, id), isNull(schema.users.deletedAt)));
  if (!u) throw Errors.notFound("User not found");
  return u;
}

/** Sets a random temporary password, ends every session of the account and returns the password once, to give to the user. */
export async function adminResetPassword(db: AppDb, actorId: string, userId: string): Promise<string> {
  const u = await targetUser(db, userId);
  const temporary = randomBytes(9).toString("base64url");
  await db.update(schema.users).set({ passwordHash: await hashPassword(temporary) }).where(eq(schema.users.id, u.id));
  await deleteAllSessions(db, u.id);
  await audit(db, actorId, "user.password_reset", u.id);
  return temporary;
}

export async function setUserSuspended(db: AppDb, actorId: string, userId: string, suspended: boolean): Promise<void> {
  if (actorId === userId) throw new AppError("self_action", 400, "You cannot suspend your own account.");
  const u = await targetUser(db, userId);
  await db.update(schema.users).set({ suspendedAt: suspended ? new Date() : null }).where(eq(schema.users.id, u.id));
  if (suspended) await deleteAllSessions(db, u.id);
  await audit(db, actorId, suspended ? "user.suspend" : "user.unsuspend", u.id);
}

export async function setUserRole(db: AppDb, actorId: string, userId: string, role: Role): Promise<void> {
  if (!ROLES.includes(role)) throw Errors.badRequest("Unknown role.");
  if (actorId === userId) throw new AppError("self_action", 400, "You cannot change your own role.");
  const u = await targetUser(db, userId);
  await db.update(schema.users).set({ role }).where(eq(schema.users.id, u.id));
  await audit(db, actorId, `user.role.${role}`, u.id);
}
