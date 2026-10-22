import { z } from "zod";
import { checkAnswer } from "@allmaths/server";
import type { CheckResponseDto } from "@/lib/lesson-types";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { renderInline, renderRich, renderStudentLatex } from "@/server/render";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.object({ answer: z.string().min(1).max(400) });

export function POST(req: Request, ctx: { params: Promise<{ lessonId: string; sectionId: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { lessonId, sectionId } = await ctx.params;
    const { db, store, engine, limits } = await getServices();
    enforce(limits.check, user.id);
    const { answer } = await readJson(req, body);
    const r = await checkAnswer({ db, store, engine }, user.id, lessonId, sectionId, answer);
    const dto: CheckResponseDto = {
      status: r.status,
      code: r.code,
      message: r.message,
      ...(r.hint ? { hintHtml: renderInline(r.hint) } : {}),
      ...(r.studentLatex ? { studentLatexHtml: renderStudentLatex(r.studentLatex) } : {}),
      ...(r.parts ? { parts: r.parts } : {}),
      ...(r.explanation ? { explanationHtml: renderRich(r.explanation) } : {}),
      ...(r.progress ? { progress: r.progress } : {}),
    };
    return json(dto);
  });
}
