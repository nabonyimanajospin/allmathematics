import { z } from "zod";
import { createPasswordReset } from "@allmaths/server";
import { assertSameOrigin, clientIp, enforce, handle, json, readJson } from "@/server/http";
import { sendResetCode } from "@/server/mailer";
import { getServices } from "@/server/runtime";

/** Always answers the same way, whether or not the e-mail belongs to an account. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const { db, limits } = await getServices();
    enforce(limits.resetRequest, clientIp(req));
    const body = await readJson(req, z.object({ email: z.string().max(254) }));
    enforce(limits.resetRequestPerEmail, body.email.trim().toLowerCase());
    const reset = await createPasswordReset(db, body.email);
    if (reset) {
      try {
        await sendResetCode(reset.email, reset.name, reset.code);
      } catch (e) {
        console.error("Could not send the reset e-mail:", e instanceof Error ? e.message : e);
      }
    }
    return json({ ok: true });
  });
}
