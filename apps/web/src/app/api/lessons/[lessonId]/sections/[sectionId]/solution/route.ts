import { revealSolution } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json } from "@/server/http";
import { renderRich } from "@/server/render";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

export function POST(req: Request, ctx: { params: Promise<{ lessonId: string; sectionId: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { lessonId, sectionId } = await ctx.params;
    const { db, store, limits } = await getServices();
    enforce(limits.hint, user.id);
    const r = await revealSolution({ db, store }, user.id, lessonId, sectionId);
    return json({ explanationHtml: renderRich(r.explanation) });
  });
}
