import { and, eq, isNull, sql } from "drizzle-orm";
import { createHash, randomBytes } from "node:crypto";
import { z } from "zod";
import { schema, type AppDb, type Role } from "@allmaths/db";
import { AppError } from "../errors";
import { dummyHash, hashPassword, verifyPassword } from "./password";

export const COMMON_PASSWORDS = new Set([
  "password12", "password123", "1234567890", "qwertyuiop", "iloveyou12", "welcome123", "letmein123", "admin12345",
]);

export const signupSchema = z.object({
  email: z.string().trim().toLowerCase().pipe(z.email().max(254)),
  name: z.string().trim().min(1, "Enter your name").max(80),
  password: z.string().min(10, "Use at least 10 characters").max(128, "Use at most 128 characters"),
});
export type SignupInput = z.infer<typeof signupSchema>;

export const signinSchema = z.object({
  email: z.string().trim().toLowerCase().pipe(z.email().max(254)),
  password: z.string().min(1).max(128),
});

export interface SessionUser {
  id: string;
  email: string;
  name: string;
  role: Role;
  locale: string;
}

const SESSION_DAYS = 30;
const REFRESH_AFTER_MS = 24 * 3600 * 1000;

export function hashToken(token: string): string {
  return createHash("sha256").update(token).digest("hex");
}

export async function registerStudent(db: AppDb, input: unknown): Promise<SessionUser> {
  const parsed = signupSchema.safeParse(input);
  if (!parsed.success) {
    throw new AppError("invalid_input", 400, parsed.error.issues[0]?.message ?? "Invalid input");
  }
  const { email, name, password } = parsed.data;
  if (COMMON_PASSWORDS.has(password.toLowerCase()) || password.toLowerCase() === email) {
    throw new AppError("weak_password", 400, "Choose a password that is harder to guess.");
  }
  const passwordHash = await hashPassword(password);
  try {
    const [row] = await db
      .insert(schema.users)
      .values({ email, name, passwordHash, role: "student" })
      .returning({
        id: schema.users.id,
        email: schema.users.email,
        name: schema.users.name,
        role: schema.users.role,
        locale: schema.users.locale,
      });
    if (!row) throw new Error("insert returned no row");
    return row;
  } catch (e) {
    if (isUniqueViolation(e)) throw new AppError("email_taken", 409, "An account with this e-mail already exists.");
    throw e;
  }
}

function isUniqueViolation(e: unknown): boolean {
  let cur: unknown = e;
  for (let i = 0; i < 4 && cur; i++) {
    if (typeof cur === "object" && cur !== null) {
      const o = cur as { code?: unknown; message?: unknown; cause?: unknown };
      if (o.code === "23505") return true;
      if (typeof o.message === "string" && /duplicate key|unique constraint/i.test(o.message)) return true;
      cur = o.cause;
    } else break;
  }
  return false;
}

/** Same message and similar time for an unknown e-mail, a wrong password and a suspended account. */
export async function authenticate(db: AppDb, input: unknown): Promise<SessionUser> {
  const parsed = signinSchema.safeParse(input);
  const fail = new AppError("invalid_credentials", 401, "E-mail or password is incorrect.");
  if (!parsed.success) throw fail;
  const { email, password } = parsed.data;
  const [u] = await db
    .select()
    .from(schema.users)
    .where(and(sql`lower(${schema.users.email}) = ${email}`, isNull(schema.users.deletedAt)))
    .limit(1);
  const ok = await verifyPassword(password, u?.passwordHash ?? (await dummyHash()));
  if (!u || !u.passwordHash || !ok || u.suspendedAt) throw fail;
  return { id: u.id, email: u.email, name: u.name, role: u.role, locale: u.locale };
}

export async function createSession(db: AppDb, userId: string, now = new Date()): Promise<{ token: string; expiresAt: Date }> {
  const token = randomBytes(32).toString("base64url");
  const expiresAt = new Date(now.getTime() + SESSION_DAYS * 24 * 3600 * 1000);
  await db.insert(schema.sessions).values({ userId, tokenHash: hashToken(token), expiresAt, lastSeenAt: now });
  return { token, expiresAt };
}

export async function validateSession(db: AppDb, token: string, now = new Date()): Promise<SessionUser | null> {
  if (!/^[A-Za-z0-9_-]{40,64}$/.test(token)) return null;
  const [row] = await db
    .select({
      sessionId: schema.sessions.id,
      expiresAt: schema.sessions.expiresAt,
      lastSeenAt: schema.sessions.lastSeenAt,
      id: schema.users.id,
      email: schema.users.email,
      name: schema.users.name,
      role: schema.users.role,
      locale: schema.users.locale,
      suspendedAt: schema.users.suspendedAt,
      deletedAt: schema.users.deletedAt,
    })
    .from(schema.sessions)
    .innerJoin(schema.users, eq(schema.users.id, schema.sessions.userId))
    .where(eq(schema.sessions.tokenHash, hashToken(token)))
    .limit(1);
  if (!row || row.expiresAt <= now || row.suspendedAt || row.deletedAt) return null;
  if (now.getTime() - row.lastSeenAt.getTime() > REFRESH_AFTER_MS) {
    await db
      .update(schema.sessions)
      .set({ lastSeenAt: now, expiresAt: new Date(now.getTime() + SESSION_DAYS * 24 * 3600 * 1000) })
      .where(eq(schema.sessions.id, row.sessionId));
  }
  return { id: row.id, email: row.email, name: row.name, role: row.role, locale: row.locale };
}

export async function deleteSession(db: AppDb, token: string): Promise<void> {
  await db.delete(schema.sessions).where(eq(schema.sessions.tokenHash, hashToken(token)));
}

export async function deleteAllSessions(db: AppDb, userId: string): Promise<void> {
  await db.delete(schema.sessions).where(eq(schema.sessions.userId, userId));
}

/** Creates (or promotes) a user with any role. For the seed script and admin tools only, never an HTTP route. */
export async function upsertUserWithRole(
  db: AppDb,
  input: { email: string; name: string; password: string; role: Role },
): Promise<string> {
  const email = input.email.trim().toLowerCase();
  const passwordHash = await hashPassword(input.password);
  const [existing] = await db.select({ id: schema.users.id }).from(schema.users).where(sql`lower(${schema.users.email}) = ${email}`);
  if (existing) {
    await db.update(schema.users).set({ name: input.name, role: input.role, passwordHash }).where(eq(schema.users.id, existing.id));
    return existing.id;
  }
  const [row] = await db.insert(schema.users).values({ email, name: input.name, role: input.role, passwordHash }).returning({ id: schema.users.id });
  if (!row) throw new Error("insert returned no row");
  return row.id;
}
