import { z } from "zod";
import { registerStudent } from "@allmaths/server";
import { assertSameOrigin, clientIp, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { startSession } from "@/server/session";

/** The e-mails (ADMIN_EMAILS, separated by commas) whose sign-up creates an administrator. */
function adminEmails(): string[] {
  return (process.env.ADMIN_EMAILS ?? "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter((e) => e !== "");
}

export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const { db, limits } = await getServices();
    enforce(limits.signUp, clientIp(req));
    const body = await readJson(req, z.unknown());
    const user = await registerStudent(db, body, { adminEmails: adminEmails() });
    await startSession(user.id);
    return json({ user: { name: user.name, email: user.email, role: user.role } }, 201);
  });
}
