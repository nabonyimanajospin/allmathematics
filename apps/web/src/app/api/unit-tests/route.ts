import { z } from "zod";
import { canOpenCourse, Errors, findExercise, getEnrolledCourseId, startUnitTest } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { renderInline, renderRich } from "@/server/render";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";
import type { StartedTestDto } from "@/lib/unit-test-types";

const body = z.strictObject({ unitId: z.string().regex(/^[a-z0-9-]{1,60}$/) });

/** Starts a unit test (or returns the one still open): 10 questions (at most 3 multiple choice) without answer keys. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, store, limits } = await getServices();
    enforce(limits.unitTest, user.id);
    const b = await readJson(req, body);
    const lessonOfUnit = store.courses.flatMap((c) => c.modules.flatMap((m) => m.units.filter((u) => u.meta.id === b.unitId).map(() => c.meta.id)))[0];
    if (!lessonOfUnit) throw Errors.notFound("Unit not found");
    if (!canOpenCourse(user.role, await getEnrolledCourseId(db, user.id), lessonOfUnit)) throw Errors.forbidden();
    const attempt = await startUnitTest(db, store, user.id, b.unitId);
    const questions = attempt.questions.map((q, index) => {
      const e = findExercise(store, q);
      if (!e) throw Errors.notFound("Question not found");
      return { index, promptHtml: renderRich(e.statement), answerType: e.answerType, ...(e.choices ? { choicesHtml: e.choices.map((c) => renderInline(c.text)) } : {}) };
    });
    const dto: StartedTestDto = { attemptId: attempt.attemptId, unitId: attempt.unitId, passScore: 7, questions };
    return json(dto);
  });
}
