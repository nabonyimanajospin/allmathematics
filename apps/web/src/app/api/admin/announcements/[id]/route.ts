import { z } from "zod";
import { deleteAnnouncement, Errors, requirePermission, setAnnouncementActive } from "@allmaths/server";
import { assertSameOrigin, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.discriminatedUnion("action", [z.strictObject({ action: z.literal("show") }), z.strictObject({ action: z.literal("hide") }), z.strictObject({ action: z.literal("delete") })]);

export function POST(req: Request, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const actor = await requireUser();
    requirePermission(actor.role, "users:manage");
    const { id } = await ctx.params;
    if (!z.uuid().safeParse(id).success) throw Errors.notFound("Announcement not found");
    const b = await readJson(req, body);
    const { db } = await getServices();
    if (b.action === "delete") await deleteAnnouncement(db, actor.id, id);
    else await setAnnouncementActive(db, actor.id, id, b.action === "show");
    return json({ ok: true });
  });
}
