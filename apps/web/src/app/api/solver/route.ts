import { z } from "zod";
import { AppError, Errors, recordSolve, solverAccess } from "@allmaths/server";
import { EngineUnavailableError } from "@allmaths/core";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { renderMath } from "@/server/render";
import { getServices } from "@/server/runtime";
import { freeSolvesPerDay } from "@/server/solver-config";
import { requireUser } from "@/server/session";
import { SOLVER_OPERATIONS, type SolveResponseDto } from "@/lib/solver-types";

const body = z.strictObject({ input: z.string().trim().min(1).max(300), operation: z.enum(SOLVER_OPERATIONS).default("auto") });

/**
 * Solves a typed problem step by step with the math engine (no AI). The free plan has a daily limit, Premium has none.
 * Only a successful solve counts; a problem the engine cannot read or solve is free.
 */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, engine, limits } = await getServices();
    enforce(limits.solver, user.id);
    const b = await readJson(req, body);
    const access = await solverAccess(db, user.id, freeSolvesPerDay());
    if (!access.premium && access.remaining === 0) {
      throw new AppError("limit_reached", 402, `You have used your ${access.limit} free solves of today. Premium has no limit.`);
    }
    let res;
    try {
      res = await engine.solve(b.input, b.operation);
    } catch (e) {
      if (e instanceof EngineUnavailableError) throw Errors.unavailable("The solver is temporarily unavailable. Please try again.", e);
      throw e;
    }
    if (!res.ok || !res.solution) {
      const dto: SolveResponseDto = { ok: false, code: res.code ?? "cannot_solve", message: res.message ?? "I could not solve this problem.", access };
      return json(dto);
    }
    await recordSolve(db, user.id, res.solution.operation);
    const after = await solverAccess(db, user.id, freeSolvesPerDay());
    const s = res.solution;
    const dto: SolveResponseDto = {
      ok: true,
      solution: {
        operation: s.operation,
        questionHtml: renderMath(s.question_latex, true),
        answerHtml: renderMath(s.answer_latex, true),
        answerText: s.answer_text,
        steps: s.steps.map((st) => ({ title: st.title, html: st.latex ? renderMath(st.latex, true) : "" })),
        notes: s.notes,
      },
      access: after,
    };
    return json(dto);
  });
}
