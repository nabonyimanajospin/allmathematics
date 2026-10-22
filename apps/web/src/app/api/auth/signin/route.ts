import { z } from "zod";
import { authenticate } from "@allmaths/server";
import { assertSameOrigin, clientIp, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { startSession } from "@/server/session";

export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const { db, limits } = await getServices();
    enforce(limits.signIn, clientIp(req));
    const body = await readJson(req, z.object({ email: z.string().max(254), password: z.string().max(128) }).loose());
    enforce(limits.signInPerEmail, body.email.trim().toLowerCase());
    const user = await authenticate(db, body);
    await startSession(user.id);
    return json({ user: { name: user.name, email: user.email, role: user.role } });
  });
}
