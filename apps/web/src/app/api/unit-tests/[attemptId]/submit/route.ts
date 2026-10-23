import { z } from "zod";
import { Errors, refreshProgress, submitUnitTest } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { renderRich } from "@/server/render";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";
import type { TestResultDto } from "@/lib/unit-test-types";

const body = z.strictObject({ answers: z.array(z.string().max(400)).min(1).max(20) });

/** Submits all the answers of a unit test: the server checks them with the math engine, stores the result and updates the progress. */
export function POST(req: Request, ctx: { params: Promise<{ attemptId: string }> }): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, store, engine, limits } = await getServices();
    enforce(limits.unitTest, user.id);
    const { attemptId } = await ctx.params;
    if (!z.uuid().safeParse(attemptId).success) throw Errors.notFound("Test not found");
    const b = await readJson(req, body);
    const result = await submitUnitTest({ db, store, engine }, user.id, attemptId, b.answers);
    await refreshProgress(db, store, user.id);
    const dto: TestResultDto = {
      score: result.score,
      total: result.total,
      passScore: result.passScore,
      passed: result.passed,
      results: result.results.map((r) => ({ index: r.index, correct: r.correct, solutionHtml: renderRich(r.solution) })),
    };
    return json(dto);
  });
}
