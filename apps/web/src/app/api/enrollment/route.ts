import { z } from "zod";
import { enrollInCourse } from "@allmaths/server";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

const body = z.strictObject({ courseId: z.string().regex(/^[a-z0-9-]{1,40}$/) });

/** Enroll in a course (or switch to another one). Progress is kept. */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, store, limits } = await getServices();
    enforce(limits.events, user.id);
    const b = await readJson(req, body);
    await enrollInCourse(db, store, user.id, b.courseId);
    return json({ ok: true });
  });
}
