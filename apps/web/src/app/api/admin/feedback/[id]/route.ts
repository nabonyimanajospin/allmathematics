import { z } from "zod";
import { deleteFeedback, Errors, requirePermission, setFeedbackStatus } from "@allmaths/server";
import { assertSameOrigin, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.discriminatedUnion("action", [
  z.strictObject({ action: z.literal("set_status"), status: z.enum(["new", "read", "resolved"]), note: z.string().max(1000).nullish() }),
  z.strictObject({ action: z.literal("delete") }),
]);

/** An administrator reads, resolves, annotates or deletes a message of a learner. */
export function POST(req: Request, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const actor = await requireUser();
    requirePermission(actor.role, "users:manage");
    const { id } = await ctx.params;
    if (!z.uuid().safeParse(id).success) throw Errors.notFound("Message not found");
    const b = await readJson(req, body);
    const { db } = await getServices();
    if (b.action === "delete") await deleteFeedback(db, actor.id, id);
    else await setFeedbackStatus(db, actor.id, id, b.status, b.note);
    return json({ ok: true });
  });
}
