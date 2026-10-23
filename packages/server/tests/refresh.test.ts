import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { and, eq } from "drizzle-orm";
import { schema } from "@allmaths/db";
import { allExercises } from "@allmaths/content-schema";
import { dbSectionId, getDashboard, readProgress, refreshProgress } from "../src";
import { makeFixture, type Fixture } from "./helpers";

const L = "mvc-m04-u01-l02";
const NOW = new Date("2026-10-23T10:00:00Z");
let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
});
afterAll(async () => {
  await f.h.close();
});

const stored = async (kind: string, id: string) => (await readProgress(f.h.db, f.userId, [{ kind: kind as "lesson", id }])).get(`${kind}:${id}`)!;

describe("progress is always recomputed from what the learner did", () => {
  it("a stale stored 100% is corrected when nothing was done", async () => {
    await f.h.db.insert(schema.progress).values([
      { userId: f.userId, objectType: "lesson", objectId: L, num: 1n, den: 1n, percent: 100 },
      { userId: f.userId, objectType: "course", objectId: "mvc", num: 1n, den: 1n, percent: 100 },
    ]);
    await refreshProgress(f.h.db, f.store, f.userId, NOW);
    expect((await stored("lesson", L)).percent).toBe(0);
    expect((await stored("course", "mvc")).percent).toBe(0);
  });

  it("all sections and all exercises but one: below 100%, and small progress is not shown as 0", async () => {
    const lesson = f.store.lesson(L)!.lesson;
    const exercises = allExercises(lesson);
    const mark = async (sectionDb: string) =>
      f.h.db.insert(schema.sectionProgress).values({ userId: f.userId, lessonId: L, sectionId: sectionDb, completedAt: NOW }).onConflictDoNothing();
    for (const s of lesson.sections) await mark(dbSectionId(L, s.id));
    for (const e of exercises.slice(0, -1)) await mark(dbSectionId(L, e.id));
    await refreshProgress(f.h.db, f.store, f.userId, NOW);
    const almost = await stored("lesson", L);
    expect(almost.percent).toBeLessThan(100);
    expect(almost.percent).toBeGreaterThan(90);
    const course = await stored("course", "mvc");
    // one 35-minute lesson of 1465 minutes is about 2.3% of the course; the tenths keep the decimal that the whole percentage drops
    expect(course.percent).toBeGreaterThanOrEqual(1);
    expect(course.percent).toBeLessThan(5);
    expect(course.tenths).toBeGreaterThanOrEqual(course.percent);

    await mark(dbSectionId(L, exercises[exercises.length - 1]!.id));
    await refreshProgress(f.h.db, f.store, f.userId, NOW);
    expect((await stored("lesson", L)).percent).toBe(100);
    expect((await stored("lesson", L)).exact).toBe("1");
  });

  it("the dashboard of an enrolled course shows the same numbers", async () => {
    const dash = await getDashboard(f.h.db, f.store, f.userId, "mvc");
    const lesson = dash.courses[0]!.modules.flatMap((m) => m.units.flatMap((u) => u.lessons)).find((l) => l.id === L)!;
    expect(lesson.percent).toBe(100);
    await f.h.db.delete(schema.progress).where(and(eq(schema.progress.userId, f.userId), eq(schema.progress.objectType, "unit")));
    const again = await getDashboard(f.h.db, f.store, f.userId, "mvc");
    const unit = again.courses[0]!.modules.find((m) => m.id === "mvc-m04")!.units.find((u) => u.id === "mvc-m04-u01")!;
    expect(unit.percent).toBeGreaterThan(0); // a deleted derived row is rebuilt from the lessons
  });
});
