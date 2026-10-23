import { z } from "zod";
import { EngineUnavailableError } from "@allmaths/core";
import { assertSameOrigin, clientIp, enforce, handle, json, readJson } from "@/server/http";
import { renderMath } from "@/server/render";
import { getServices } from "@/server/runtime";

const body = z.strictObject({
  lines: z.record(z.string().regex(/^[1-8]$/), z.string().max(200)).refine((o) => Object.keys(o).length <= 8),
  params: z.record(z.string().regex(/^[a-z]$/), z.string().regex(/^-?\d{1,6}(\/\d{1,3})?$/)).default({}),
  candidates: z.array(z.strictObject({ lines: z.array(z.number().int().min(1).max(8)).min(1).max(2), x: z.number().finite() })).max(24),
});

export interface ExactPointDto {
  lines: number[];
  x: number;
  html: string;
  text: string;
}

/**
 * Makes the roots and intersections that the grapher found numerically exact, when the math engine can prove the exact value.
 * Open to everyone (the grapher needs no account), so it is limited per address.
 */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const { engine, limits } = await getServices();
    enforce(limits.solver, `graph:${clientIp(req)}`);
    const b = await readJson(req, body);
    if (b.candidates.length === 0) return json({ points: [] as ExactPointDto[] });
    try {
      const res = await engine.graphExact(b);
      const points: ExactPointDto[] = res.points.map((p) => ({
        lines: p.lines,
        x: p.x,
        html: renderMath(String.raw`\left(${p.x_latex},\ ${p.y_latex}\right)`, false),
        text: `(${p.x_text}, ${p.y_text})`,
      }));
      return json({ points });
    } catch (e) {
      if (e instanceof EngineUnavailableError) return json({ points: [] as ExactPointDto[] });
      throw e;
    }
  });
}
