import { NextResponse } from "next/server";
import { AppError, Errors, type RateLimiter } from "@allmaths/server";
import type { z } from "zod";

const MAX_BODY_BYTES = 32 * 1024;

export function json<T>(data: T, status = 200, headers?: Record<string, string>): NextResponse {
  return NextResponse.json(data, { status, headers: { "cache-control": "no-store", ...headers } });
}

/** Wraps a route handler: known errors become a JSON error, unknown ones are logged and hidden. */
export async function handle(fn: () => Promise<Response>): Promise<Response> {
  try {
    return await fn();
  } catch (e) {
    if (e instanceof AppError) {
      return json({ error: { code: e.code, message: e.message } }, e.status);
    }
    // the browser cancelled the request (page left, beacon): nothing to report
    if (e instanceof Error && e.message === "aborted") return new Response(null, { status: 499 });
    console.error("Unhandled error in route:", e instanceof Error ? e.stack : e);
    return json({ error: { code: "server_error", message: "Something went wrong. Please try again." } }, 500);
  }
}

/**
 * CSRF defence for state-changing requests (cookies are SameSite=Lax as well): the request must come
 * from our own origin. `Origin` is checked; if a browser omits it, `Sec-Fetch-Site` must say same-origin.
 */
export function assertSameOrigin(req: Request): void {
  const host = req.headers.get("x-forwarded-host") ?? req.headers.get("host");
  const origin = req.headers.get("origin");
  if (origin) {
    let originHost: string;
    try {
      originHost = new URL(origin).host;
    } catch {
      throw new AppError("bad_origin", 403, "Request blocked.");
    }
    if (originHost !== host) throw new AppError("bad_origin", 403, "Request blocked.");
    return;
  }
  if (req.headers.get("sec-fetch-site") === "same-origin") return;
  throw new AppError("bad_origin", 403, "Request blocked.");
}

export async function readJson<S extends z.ZodType>(req: Request, schema: S): Promise<z.infer<S>> {
  const length = Number(req.headers.get("content-length") ?? "0");
  if (length > MAX_BODY_BYTES) throw new AppError("too_large", 413, "Request too large.");
  const text = await req.text();
  if (text.length > MAX_BODY_BYTES) throw new AppError("too_large", 413, "Request too large.");
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    throw Errors.badRequest("Invalid JSON.", "invalid_json");
  }
  const parsed = schema.safeParse(raw);
  if (!parsed.success) throw Errors.badRequest(parsed.error.issues[0]?.message ?? "Invalid request.", "invalid_input");
  return parsed.data;
}

export function clientIp(req: Request): string {
  const fwd = req.headers.get("x-forwarded-for");
  return (fwd?.split(",")[0] ?? req.headers.get("x-real-ip") ?? "local").trim();
}

export function enforce(limiter: RateLimiter, key: string): void {
  const r = limiter.hit(key);
  if (!r.allowed) throw Errors.tooMany(r.retryAfterMs);
}
