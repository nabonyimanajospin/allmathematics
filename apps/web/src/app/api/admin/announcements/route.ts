import { z } from "zod";
import { createAnnouncement, requirePermission } from "@allmaths/server";
import { assertSameOrigin, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.strictObject({ message: z.string().max(600) });

/** An administrator writes an announcement that every signed-in learner sees until it is hidden. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const actor = await requireUser();
    requirePermission(actor.role, "users:manage");
    const b = await readJson(req, body);
    const { db } = await getServices();
    return json({ ok: true, id: await createAnnouncement(db, actor.id, b.message) }, 201);
  });
}
