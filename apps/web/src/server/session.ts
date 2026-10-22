import { cookies } from "next/headers";
import { cache } from "react";
import { createSession, deleteSession, Errors, validateSession, type SessionUser } from "@allmaths/server";
import { getServices } from "./runtime";

export const SESSION_COOKIE = "allmaths_session";

function secureCookies(): boolean {
  return process.env.NODE_ENV === "production" && process.env.SESSION_COOKIE_SECURE !== "false";
}

export async function startSession(userId: string): Promise<void> {
  const { db } = await getServices();
  const { token, expiresAt } = await createSession(db, userId);
  (await cookies()).set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: secureCookies(),
    path: "/",
    expires: expiresAt,
  });
}

export async function endSession(): Promise<void> {
  const jar = await cookies();
  const token = jar.get(SESSION_COOKIE)?.value;
  if (token) {
    const { db } = await getServices();
    await deleteSession(db, token);
  }
  jar.set(SESSION_COOKIE, "", { httpOnly: true, sameSite: "lax", secure: secureCookies(), path: "/", maxAge: 0 });
}

/** The signed-in user for this request, or null. Cached per request. */
export const getCurrentUser = cache(async (): Promise<SessionUser | null> => {
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  if (!token) return null;
  const { db } = await getServices();
  return validateSession(db, token);
});

export async function requireUser(): Promise<SessionUser> {
  const user = await getCurrentUser();
  if (!user) throw Errors.unauthorized();
  return user;
}

/** Only same-site relative paths are accepted as a post-login destination (no open redirect). */
export function safeNext(next: string | null | undefined, fallback = "/dashboard"): string {
  if (!next || !next.startsWith("/") || next.startsWith("//") || next.includes("\\")) return fallback;
  return next;
}
