import { Errors, getLessonState } from "@allmaths/server";
import { handle, json } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

export function GET(_req: Request, ctx: { params: Promise<{ lessonId: string }> }): Promise<Response> {
  return handle(async () => {
    const user = await requireUser();
    const { lessonId } = await ctx.params;
    const { db, store } = await getServices();
    const state = await getLessonState(db, store, user.id, lessonId);
    if (!state) throw Errors.notFound("Lesson not found");
    return json(state);
  });
}
