import { z } from "zod";
import { getHint } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { renderRich } from "@/server/render";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.object({ index: z.number().int().min(0).max(2) });

export function POST(req: Request, ctx: { params: Promise<{ lessonId: string; sectionId: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { lessonId, sectionId } = await ctx.params;
    const { db, store, limits } = await getServices();
    enforce(limits.hint, user.id);
    const { index } = await readJson(req, body);
    const hint = await getHint({ db, store }, user.id, lessonId, sectionId, index);
    return json({ textHtml: renderRich(hint.text), hintsUsed: hint.hintsUsed, hintCount: hint.hintCount });
  });
}
