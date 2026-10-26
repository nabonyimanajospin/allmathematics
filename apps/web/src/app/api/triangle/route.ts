import { z } from "zod";
import { Errors } from "@allmaths/server";
import { EngineUnavailableError } from "@allmaths/core";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";
import { toTriangleDto } from "@/server/triangle";
import type { TriangleResponseDto } from "@/lib/triangle-types";

const coordinate = z.string().trim().min(1).max(24);
const body = z.strictObject({ points: z.array(z.tuple([coordinate, coordinate])).length(3) });

/**
 * Everything about a triangle from its three vertices, computed exactly by the math engine (no decimals).
 * Part of the learner's account, and limited per learner like the other tools.
 */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { engine, limits } = await getServices();
    enforce(limits.solver, `triangle:${user.id}`);
    const b = await readJson(req, body);
    let res;
    try {
      res = await engine.triangle(b.points);
    } catch (e) {
      if (e instanceof EngineUnavailableError) throw Errors.unavailable("The triangle tool is temporarily unavailable. Please try again.", e);
      throw e;
    }
    if (!res.ok || !res.data) {
      const dto: TriangleResponseDto = { ok: false, code: res.code ?? "cannot_analyze", message: res.message ?? "I could not analyze this triangle." };
      return json(dto);
    }
    const dto: TriangleResponseDto = { ok: true, data: toTriangleDto(res.data) };
    return json(dto);
  });
}
