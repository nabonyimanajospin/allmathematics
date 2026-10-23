import { z } from "zod";
import { ROLES } from "@allmaths/db";
import { adminResetPassword, Errors, requirePermission, setUserRole, setUserSuspended } from "@allmaths/server";
import { assertSameOrigin, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.discriminatedUnion("action", [
  z.strictObject({ action: z.literal("reset_password") }),
  z.strictObject({ action: z.literal("suspend") }),
  z.strictObject({ action: z.literal("unsuspend") }),
  z.strictObject({ action: z.literal("set_role"), role: z.enum(ROLES) }),
]);

/** Account actions of an administrator. The temporary password is returned once and never stored in clear. */
export function POST(req: Request, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const actor = await requireUser();
    requirePermission(actor.role, "users:manage");
    const { id } = await ctx.params;
    if (!z.uuid().safeParse(id).success) throw Errors.notFound("User not found");
    const b = await readJson(req, body);
    const { db } = await getServices();
    switch (b.action) {
      case "reset_password":
        return json({ ok: true, temporaryPassword: await adminResetPassword(db, actor.id, id) });
      case "suspend":
        await setUserSuspended(db, actor.id, id, true);
        return json({ ok: true });
      case "unsuspend":
        await setUserSuspended(db, actor.id, id, false);
        return json({ ok: true });
      case "set_role":
        await setUserRole(db, actor.id, id, b.role);
        return json({ ok: true });
    }
  });
}
