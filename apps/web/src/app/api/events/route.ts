import { eventBatchSchema } from "@allmaths/core";
import { getLessonState, ingestEvents } from "@allmaths/server";
import type { LessonStateDto } from "@/lib/lesson-types";
import { assertSameOrigin, enforce, handle, json, readJson } from "@/server/http";
import { getServices } from "@/server/runtime";
import { requireUser } from "@/server/session";

/** Batched learning events from the lesson player (also sent with navigator.sendBeacon on page exit). */
export function POST(req: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(req);
    const user = await requireUser();
    const { db, store, limits } = await getServices();
    enforce(limits.events, user.id);
    const batch = await readJson(req, eventBatchSchema);
    const result = await ingestEvents(db, store, user.id, batch.events);

    // The authoritative state of every lesson in the batch, so the browser can reconcile its optimistic UI.
    const states: Record<string, LessonStateDto> = {};
    for (const lessonId of new Set(batch.events.map((e) => e.lessonId))) {
      const s = await getLessonState(db, store, user.id, lessonId);
      if (s) {
        states[lessonId] = {
          completedSectionIds: s.completedSectionIds,
          solvedExerciseIds: s.solvedExerciseIds,
          hintsUsed: s.hintsUsed,
          completedChoices: s.completedChoices,
          resumeSectionId: s.resumeSectionId,
          progress: s.progress,
        };
      }
    }
    return json({ accepted: result.accepted, duplicates: result.duplicates, rejected: result.rejected.length, states });
  });
}
