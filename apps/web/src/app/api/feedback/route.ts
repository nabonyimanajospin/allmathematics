import { z } from "zod";
import { FEEDBACK_MAX, submitFeedback } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.strictObject({
  category: z.string().min(1).max(20),
  message: z.string().max(FEEDBACK_MAX + 200),
  page: z.string().max(200).nullish(),
});

/** A signed-in learner sends a message to the administrators. A few per ten minutes. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, limits } = await getServices();
    enforce(limits.feedback, user.id);
    const b = await readJson(req, body);
    const id = await submitFeedback(db, user.id, { category: b.category, message: b.message, page: b.page ?? null });
    return json({ ok: true, id }, 201);
  });
}
