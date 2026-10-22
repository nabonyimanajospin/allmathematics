import { randomUUID } from "node:crypto";
import { resolve } from "node:path";
import { createEngineClient, requiredSeconds, type EventInput } from "@allmaths/core";
import { schema, type DbHandle } from "@allmaths/db";
import { openTestDb } from "@allmaths/db/testing";
import { buildStore, loadStore, syncContent, ingestEvents, checkAnswer, type ContentStore } from "../src";

export const contentDir = resolve(import.meta.dirname, "..", "..", "..", "content");

export interface Fixture {
  h: DbHandle;
  store: ContentStore;
  userId: string;
}

/** The progress formulas are tested on the first three lessons of Geometry only, so that its numbers stay fixed as content grows. */
export function geometryModule1Store(): ContentStore {
  const full = loadStore(contentDir);
  const geo = full.courses.find((c) => c.meta.id === "geo")!;
  const first = geo.modules
    .filter((m) => m.meta.id === "geo-m01")
    .map((m) => ({
      ...m,
      units: m.units
        .filter((u) => u.meta.id === "geo-m01-u01")
        .map((u) => ({ ...u, lessons: u.lessons.filter((l) => ["geo-m01-u01-l01", "geo-m01-u01-l02", "geo-m01-u01-l03"].includes(l.meta.id)) })),
    }));
  return buildStore([{ ...geo, modules: first }]);
}

export async function makeFixture(options: { geometryModule1Only?: boolean } = {}): Promise<Fixture> {
  const h = await openTestDb();
  const store = options.geometryModule1Only ? geometryModule1Store() : loadStore(contentDir);
  await syncContent(h.db, store);
  const [u] = await h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "T" }).returning();
  return { h, store, userId: u!.id };
}

export const engine = createEngineClient({
  url: process.env.MATH_ENGINE_URL ?? "http://127.0.0.1:8001",
  token: process.env.MATH_ENGINE_TOKEN ?? "dev-engine-token",
  timeoutMs: 20_000,
});

export const ev = (o: Partial<EventInput> & Pick<EventInput, "verb" | "lessonId">): EventInput => ({
  eventId: randomUUID(),
  clientTimestamp: Date.now(),
  ...o,
});

/** Read a section as a student would: open it, then report its minimum active time. */
export async function readSection(f: Fixture, lessonId: string, sectionId: string, at: Date): Promise<void> {
  const s = f.store.lesson(lessonId)!.lesson.sections.find((x) => x.id === sectionId)!;
  const secs = requiredSeconds({ type: s.type, minSeconds: s.minSeconds });
  await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId, sectionId })], at);
  await ingestEvents(
    f.h.db,
    f.store,
    f.userId,
    [ev({ verb: "viewed", lessonId, sectionId, result: { durationMs: secs * 1000 } })],
    new Date(at.getTime() + secs * 1000),
  );
}

/** Do everything in a lesson: read the content, answer checks with the true key. Returns the end time. */
export async function completeLesson(f: Fixture, lessonId: string, start = new Date("2026-10-21T10:00:00Z")): Promise<Date> {
  let t = start;
  for (const s of f.store.lesson(lessonId)!.lesson.sections) {
    if (s.type === "check") {
      const answer = s.answerType === "multiple_choice" ? String(s.correctIndex) : s.answer;
      const r = await checkAnswer({ db: f.h.db, store: f.store, engine }, f.userId, lessonId, s.id, answer, t);
      if (r.status !== "correct") throw new Error(`check ${s.id} not correct: ${r.code} ${r.message}`);
    } else {
      await readSection(f, lessonId, s.id, t);
      t = new Date(t.getTime() + requiredSeconds({ type: s.type, minSeconds: s.minSeconds }) * 1000 + 1000);
    }
  }
  return t;
}
