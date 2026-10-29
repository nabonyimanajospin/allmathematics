import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { schema } from "@allmaths/db";
import { dbSectionId, findExercise, findExerciseTask, getLessonState, hasUnitTest, unitTestBank } from "../src";
import { makeFixture, type Fixture } from "./helpers";

// The first quick check of this lesson, "Which surface is z = x^2 - y^2?", is multiple choice and its second option (index 1) is right.
const LESSON = "geo-m03-u04-l01";
let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
});
afterAll(async () => {
  await f.h.close();
});

describe("a multiple-choice question that was answered correctly", () => {
  it("is listed with its chosen option only after the answer, so the page can show it as selected", async () => {
    const before = await getLessonState(f.h.db, f.store, f.userId, LESSON);
    expect(before?.completedChoices).toEqual({});

    await f.h.db.insert(schema.sectionProgress).values({ userId: f.userId, lessonId: LESSON, sectionId: dbSectionId(LESSON, "chk-type"), completedAt: new Date("2026-10-23T10:00:00Z") });
    const after = await getLessonState(f.h.db, f.store, f.userId, LESSON);
    expect(after?.completedChoices).toEqual({ "chk-type": 1 });
  });

  it("is also listed for an exercise of a practice set that was solved", async () => {
    const lesson = f.store.lesson(LESSON)!.lesson;
    const choice = lesson.exerciseSets.flatMap((s) => s.items).find((e) => e.answerType === "multiple_choice");
    if (!choice) return; // this lesson has no multiple-choice exercise: nothing more to check
    await f.h.db.insert(schema.sectionProgress).values({ userId: f.userId, lessonId: LESSON, sectionId: dbSectionId(LESSON, choice.id), completedAt: new Date("2026-10-23T10:05:00Z") });
    const state = await getLessonState(f.h.db, f.store, f.userId, LESSON);
    expect(state?.completedChoices[choice.id]).toBe(choice.correctIndex);
  });
});

describe("the instruction of a test question", () => {
  it("every question of every unit test has the instruction of its exercise set (many statements are only an equation)", () => {
    let checked = 0;
    for (const course of f.store.courses)
      for (const m of course.modules)
        for (const u of m.units) {
          if (!hasUnitTest(f.store, u.meta.id)) continue;
          for (const q of unitTestBank(f.store, u.meta.id)) {
            expect(findExercise(f.store, q), `${q.lessonId}/${q.exerciseId}`).toBeDefined();
            const task = findExerciseTask(f.store, q);
            expect(task && task.trim().length > 0, `${q.lessonId}/${q.exerciseId} has no instruction`).toBe(true);
            checked++;
          }
        }
    expect(checked).toBeGreaterThan(1500);
  });

  it("gives the instruction of the first-order partial derivatives set to a question that is only a function", () => {
    const bank = unitTestBank(f.store, "mvc-m01-u02");
    const task = bank.map((q) => findExerciseTask(f.store, q)).find((t) => t?.startsWith("Calculate the partial derivatives of the first order"));
    expect(task).toBeDefined();
  });
});
