/** "Forgot password": a 6-digit one-time code sent by e-mail, valid for 10 minutes, 5 tries. */

import { and, desc, eq, isNull, sql } from "drizzle-orm";
import { createHash, randomInt, timingSafeEqual } from "node:crypto";
import { z } from "zod";
import { schema, type AppDb } from "@allmaths/db";
import { AppError } from "../errors";
import { hashPassword } from "./password";
import { COMMON_PASSWORDS, deleteAllSessions } from "./users";

export const RESET_CODE_MINUTES = 10;
export const RESET_MAX_ATTEMPTS = 5;

const emailSchema = z.string().trim().toLowerCase().pipe(z.email().max(254));

function hashCode(resetId: string, code: string): string {
  return createHash("sha256").update(`${resetId}:${code}`).digest("hex");
}

/**
 * Creates a code for the account with this e-mail and returns it so the caller can send it.
 * Returns null when there is no active account: the caller answers the same way in both cases,
 * so the form never reveals which e-mails are registered.
 */
export async function createPasswordReset(db: AppDb, emailInput: string, now = new Date()): Promise<{ email: string; name: string; code: string } | null> {
  const parsed = emailSchema.safeParse(emailInput);
  if (!parsed.success) return null;
  const email = parsed.data;
  const [u] = await db
    .select({ id: schema.users.id, email: schema.users.email, name: schema.users.name, suspendedAt: schema.users.suspendedAt })
    .from(schema.users)
    .where(and(sql`lower(${schema.users.email}) = ${email}`, isNull(schema.users.deletedAt)))
    .limit(1);
  if (!u || u.suspendedAt) return null;
  // a new code replaces the older ones
  await db.update(schema.passwordResets).set({ usedAt: now }).where(and(eq(schema.passwordResets.userId, u.id), isNull(schema.passwordResets.usedAt)));
  const code = String(randomInt(0, 1_000_000)).padStart(6, "0");
  const [row] = await db
    .insert(schema.passwordResets)
    .values({ userId: u.id, codeHash: "", expiresAt: new Date(now.getTime() + RESET_CODE_MINUTES * 60_000) })
    .returning({ id: schema.passwordResets.id });
  if (!row) throw new Error("insert returned no row");
  await db.update(schema.passwordResets).set({ codeHash: hashCode(row.id, code) }).where(eq(schema.passwordResets.id, row.id));
  return { email: u.email, name: u.name, code };
}

const resetSchema = z.object({
  email: emailSchema,
  code: z.string().trim().regex(/^\d{6}$/, "Enter the 6-digit code."),
  password: z.string().min(10, "Use at least 10 characters").max(128, "Use at most 128 characters"),
});

/** Checks the code and sets the new password. All sessions of the account end. */
export async function completePasswordReset(db: AppDb, input: unknown, now = new Date()): Promise<void> {
  const parsed = resetSchema.safeParse(input);
  if (!parsed.success) throw new AppError("invalid_input", 400, parsed.error.issues[0]?.message ?? "Invalid input");
  const { email, code, password } = parsed.data;
  const bad = new AppError("invalid_code", 400, "The code is wrong or has expired. Ask for a new one.");
  if (COMMON_PASSWORDS.has(password.toLowerCase()) || password.toLowerCase() === email) {
    throw new AppError("weak_password", 400, "Choose a password that is harder to guess.");
  }
  const [row] = await db
    .select({ id: schema.passwordResets.id, userId: schema.passwordResets.userId, codeHash: schema.passwordResets.codeHash, expiresAt: schema.passwordResets.expiresAt, attempts: schema.passwordResets.attempts })
    .from(schema.passwordResets)
    .innerJoin(schema.users, eq(schema.users.id, schema.passwordResets.userId))
    .where(and(sql`lower(${schema.users.email}) = ${email}`, isNull(schema.users.deletedAt), isNull(schema.users.suspendedAt), isNull(schema.passwordResets.usedAt)))
    .orderBy(desc(schema.passwordResets.createdAt))
    .limit(1);
  if (!row || row.expiresAt <= now || row.attempts >= RESET_MAX_ATTEMPTS) throw bad;
  const expected = Buffer.from(row.codeHash, "hex");
  const given = Buffer.from(hashCode(row.id, code), "hex");
  const same = expected.length === given.length && timingSafeEqual(expected, given);
  if (!same) {
    await db.update(schema.passwordResets).set({ attempts: row.attempts + 1 }).where(eq(schema.passwordResets.id, row.id));
    throw bad;
  }
  const passwordHash = await hashPassword(password);
  await db.update(schema.users).set({ passwordHash }).where(eq(schema.users.id, row.userId));
  await db.update(schema.passwordResets).set({ usedAt: now }).where(eq(schema.passwordResets.id, row.id));
  await deleteAllSessions(db, row.userId);
}
