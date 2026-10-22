import { z } from "zod";
import { setFormulaSaved } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.strictObject({ lessonId: z.string().min(1).max(80), sectionId: z.string().min(1).max(80), saved: z.boolean() });

/** Save a formula or a theorem to the formula sheet, or remove it. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, store, limits } = await getServices();
    enforce(limits.events, user.id);
    const b = await readJson(req, body);
    await setFormulaSaved(db, store, user.id, b.lessonId, b.sectionId, b.saved);
    return json({ ok: true });
  });
}
