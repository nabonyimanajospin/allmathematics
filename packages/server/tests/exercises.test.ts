import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { eq } from "drizzle-orm";
import { schema } from "@allmaths/db";
import { toClientLesson } from "@allmaths/content-schema";
import { allExercises } from "@allmaths/content-schema";
import { checkAnswer, dbSectionId, getHint, getLessonState, recomputeProgress } from "../src";
import { engine, makeFixture, type Fixture } from "./helpers";

// Lesson "Separable equations" of Module 4 has an exercise set from the printed sheet.
const L = "mvc-m04-u01-l02";
const T0 = new Date("2026-10-21T10:00:00Z");

let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
  if (!(await engine.health())) {
    if (process.env.REQUIRE_ENGINE === "1") throw new Error("Math engine is required but not running");
    throw new Error("Start the math engine on :8001 (see docs/running.md) to run these tests");
  }
});
afterAll(async () => {
  await f.h.close();
});

const deps = () => ({ db: f.h.db, store: f.store, engine });
const percent = async () => (await getLessonState(f.h.db, f.store, f.userId, L))!.progress.lesson.percent;

describe("exercises of a lesson", () => {
  it("a wrong answer is recorded but gives no practice credit", async () => {
    const before = await percent();
    const r = await checkAnswer(deps(), f.userId, L, "sep-e", "y = C*cos(x)", T0);
    expect(r.status).toBe("incorrect");
    expect(r.explanation).toBeUndefined();
    expect(await percent()).toBe(before);
  });

  it("a correct general solution is accepted in an equivalent form and shows the worked solution", async () => {
    const r = await checkAnswer(deps(), f.userId, L, "sep-e", "y = K sin(x)", T0);
    expect(r.status).toBe("correct");
    expect(r.explanation).toContain("\\sin x");
    expect(await percent()).toBeGreaterThan(0);
  });

  it("solving the same exercise again does not raise the progress twice", async () => {
    const before = await percent();
    const r = await checkAnswer(deps(), f.userId, L, "sep-e", "y = C*sin(x)", new Date(T0.getTime() + 60_000));
    expect(r.status).toBe("correct");
    expect(await percent()).toBe(before);
    const rows = await f.h.db.select().from(schema.sectionProgress).where(eq(schema.sectionProgress.userId, f.userId));
    expect(rows.filter((x) => x.sectionId.endsWith("sep-e"))).toHaveLength(1);
  });

  it("a solution without an arbitrary constant is not a general solution", async () => {
    const r = await checkAnswer(deps(), f.userId, L, "sep-e", "y = sin(x)", T0);
    expect(r.status).not.toBe("correct");
  });

  it("an initial-value problem needs the particular solution", async () => {
    expect((await checkAnswer(deps(), f.userId, L, "sep-g", "y = sqrt(2*ln(1+e^x) - 2*ln(2) + 1)", T0)).status).toBe("correct");
    expect((await checkAnswer(deps(), f.userId, L, "sep-g", "y^2 = 2*ln(1+e^x) + C", T0)).status).not.toBe("correct");
  });

  it("hints are available for an exercise, one at a time", async () => {
    const h = await getHint(deps(), f.userId, L, "sep-a", 0, T0);
    expect(h.text.length).toBeGreaterThan(0);
  });

  it("the browser version of the lesson never carries an answer key", () => {
    const client = toClientLesson(f.store.lesson(L)!.lesson);
    const text = JSON.stringify(client);
    expect(text).not.toContain("C*sin(x)");
    const items = client.exerciseSets.flatMap((s) => s.items);
    expect(items.length).toBeGreaterThanOrEqual(8);
    for (const item of items) {
      expect(item).not.toHaveProperty("answer");
      expect(item).not.toHaveProperty("solution");
    }
  });

  it("an exercise can name a parameter that is given in the problem", async () => {
    const lin = "mvc-m04-u01-l04";
    const ok = await checkAnswer(deps(), f.userId, lin, "lin-e", "y = x^n*(e^x + C)", T0);
    expect(ok.status).toBe("correct");
    const bad = await checkAnswer(deps(), f.userId, lin, "lin-e", "y = x^n*e^x", T0);
    expect(bad.status).not.toBe("correct");
  });
  it("the lesson reaches 100% only when every section is read and every exercise is solved", async () => {
    const lesson = f.store.lesson(L)!.lesson;
    const exercises = allExercises(lesson);
    expect(exercises.length).toBeGreaterThan(1);
    const done = async (sectionDb: string, at: Date) => {
      await f.h.db
        .insert(schema.sectionProgress)
        .values({ userId: f.userId, lessonId: L, sectionId: sectionDb, completedAt: at })
        .onConflictDoUpdate({ target: [schema.sectionProgress.userId, schema.sectionProgress.sectionId], set: { completedAt: at } });
    };
    const at = new Date(T0.getTime() + 3_600_000);
    for (const sec of lesson.sections) await done(dbSectionId(L, sec.id), at);
    for (const ex of exercises.slice(0, -1)) await done(dbSectionId(L, ex.id), at);
    const almost = await recomputeProgress(f.h.db, f.store, f.userId, L, at);
    expect(almost.lesson.percent).toBeLessThan(100);
    expect(almost.course.percent).toBeLessThan(100);
    await done(dbSectionId(L, exercises[exercises.length - 1]!.id), at);
    const all = await recomputeProgress(f.h.db, f.store, f.userId, L, at);
    expect(all.lesson.percent).toBe(100);
    expect(all.lesson.exact).toBe("1");
  });
});
