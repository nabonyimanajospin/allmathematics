/**
 * Who may use the solver and how much. The free plan has a few solves per day; Premium has no limit.
 * Premium comes from a subscription row (an administrator grants it by hand, or a payment provider creates it after a verified payment).
 */

import { and, count, eq, gte, or, isNull, gt } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import { Errors } from "../errors";

export const DEFAULT_FREE_SOLVES_PER_DAY = 5;
const DAY_MS = 24 * 3_600_000;

export interface SolverAccess {
  premium: boolean;
  /** Solves used in the last 24 hours. */
  used: number;
  /** The free limit, or null for Premium (no limit). */
  limit: number | null;
  /** Solves left, or null for Premium. */
  remaining: number | null;
}

export async function hasPremium(db: AppDb, userId: string, now = new Date()): Promise<boolean> {
  const rows = await db
    .select({ id: schema.subscriptions.id })
    .from(schema.subscriptions)
    .where(
      and(
        eq(schema.subscriptions.userId, userId),
        eq(schema.subscriptions.status, "active"),
        eq(schema.subscriptions.plan, "premium"),
        or(isNull(schema.subscriptions.currentPeriodEnd), gt(schema.subscriptions.currentPeriodEnd, now)),
      ),
    )
    .limit(1);
  return rows.length > 0;
}

export async function solverAccess(db: AppDb, userId: string, freeLimit = DEFAULT_FREE_SOLVES_PER_DAY, now = new Date()): Promise<SolverAccess> {
  const [premium, used] = await Promise.all([
    hasPremium(db, userId, now),
    db
      .select({ n: count() })
      .from(schema.solverRequests)
      .where(and(eq(schema.solverRequests.userId, userId), gte(schema.solverRequests.createdAt, new Date(now.getTime() - DAY_MS)))),
  ]);
  const n = used[0]?.n ?? 0;
  if (premium) return { premium: true, used: n, limit: null, remaining: null };
  return { premium: false, used: n, limit: freeLimit, remaining: Math.max(0, freeLimit - n) };
}

export async function recordSolve(db: AppDb, userId: string, operation: string, now = new Date()): Promise<void> {
  await db.insert(schema.solverRequests).values({ userId, operation: operation.slice(0, 40), createdAt: now });
}

/** An administrator gives a learner Premium for a number of days (a payment provider does the same after a verified payment). */
export async function grantPremium(db: AppDb, actorId: string, userId: string, days: number, now = new Date()): Promise<Date> {
  if (!Number.isInteger(days) || days < 1 || days > 3650) throw Errors.badRequest("Choose between 1 and 3650 days.", "invalid_days");
  const [u] = await db.select({ id: schema.users.id }).from(schema.users).where(eq(schema.users.id, userId));
  if (!u) throw Errors.notFound("User not found");
  const end = new Date(now.getTime() + days * DAY_MS);
  await db.insert(schema.subscriptions).values({ userId, provider: "manual", status: "active", plan: "premium", currentPeriodEnd: end });
  await db.insert(schema.auditLog).values({ actorId, action: "premium.grant", target: userId });
  return end;
}

export async function revokePremium(db: AppDb, actorId: string, userId: string): Promise<void> {
  await db
    .update(schema.subscriptions)
    .set({ status: "canceled" })
    .where(and(eq(schema.subscriptions.userId, userId), eq(schema.subscriptions.plan, "premium"), eq(schema.subscriptions.status, "active")));
  await db.insert(schema.auditLog).values({ actorId, action: "premium.revoke", target: userId });
}
