import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { randomUUID } from "node:crypto";
import { schema } from "@allmaths/db";
import { allExercises } from "@allmaths/content-schema";
import {
  UNIT_TEST_PASS,
  UNIT_TEST_QUESTIONS,
  dbSectionId,
  findExercise,
  getDashboard,
  hasUnitTest,
  pickQuestions,
  refreshProgress,
  readProgress,
  startUnitTest,
  submitUnitTest,
  unitTestBank,
  unitTestStatus,
  type TestQuestionRef,
} from "../src";
import { engine, makeFixture, type Fixture } from "./helpers";

const UNIT = "geo-m01-u01";
const NOW = new Date("2026-10-23T10:00:00Z");
let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
  if (!(await engine.health())) throw new Error("Start the math engine on :8001 (see docs/running.md) to run these tests");
});
afterAll(async () => {
  await f.h.close();
});

const deps = () => ({ db: f.h.db, store: f.store, engine });
const keyOf = (q: TestQuestionRef) => findExercise(f.store, q)!.answer;

describe("drawing the questions", () => {
  it("the bank has typed-answer exercises only, from the lessons of the unit", () => {
    const bank = unitTestBank(f.store, UNIT);
    expect(bank.length).toBeGreaterThanOrEqual(UNIT_TEST_QUESTIONS);
    expect(new Set(bank.map((q) => q.lessonId))).toEqual(new Set(["geo-m01-u01-l01", "geo-m01-u01-l02", "geo-m01-u01-l03", "geo-m01-u01-l04"]));
    for (const q of bank) expect(findExercise(f.store, q)!.answerType).not.toBe("multiple_choice");
    expect(hasUnitTest(f.store, UNIT)).toBe(true);
  });

  it("picks 10 different questions spread over the lessons, and avoids the previous ones", () => {
    const bank = unitTestBank(f.store, UNIT);
    const first = pickQuestions(bank, UNIT_TEST_QUESTIONS);
    expect(new Set(first.map((q) => `${q.lessonId}/${q.exerciseId}`)).size).toBe(UNIT_TEST_QUESTIONS);
    const perLesson = new Map<string, number>();
    for (const q of first) perLesson.set(q.lessonId, (perLesson.get(q.lessonId) ?? 0) + 1);
    expect(Math.max(...perLesson.values()) - Math.min(...perLesson.values())).toBeLessThanOrEqual(1);
    const second = pickQuestions(bank, UNIT_TEST_QUESTIONS, first);
    const used = new Set(first.map((q) => `${q.lessonId}/${q.exerciseId}`));
    expect(second.filter((q) => used.has(`${q.lessonId}/${q.exerciseId}`)).length).toBe(0);
  });
});

describe("taking the test", () => {
  it("starting twice gives the same open attempt; the other learner has their own", async () => {
    const a = await startUnitTest(f.h.db, f.store, f.userId, UNIT, NOW);
    const b = await startUnitTest(f.h.db, f.store, f.userId, UNIT, new Date(NOW.getTime() + 60_000));
    expect(b.attemptId).toBe(a.attemptId);
    expect(a.questions).toHaveLength(UNIT_TEST_QUESTIONS);
    const [other] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "Other" }).returning();
    const c = await startUnitTest(f.h.db, f.store, other!.id, UNIT, NOW);
    expect(c.attemptId).not.toBe(a.attemptId);
    await expect(submitUnitTest(deps(), other!.id, a.attemptId, a.questions.map(() => "1"))).rejects.toMatchObject({ code: "not_found" });
  });

  it("6 correct answers do not pass, 7 do, and an attempt can be submitted only once", async () => {
    const first = await startUnitTest(f.h.db, f.store, f.userId, UNIT, NOW);
    const answersFor = (n: number, q: TestQuestionRef[]) => q.map((x, i) => (i < n ? keyOf(x) : "987654321"));
    const six = await submitUnitTest(deps(), f.userId, first.attemptId, answersFor(6, first.questions), NOW);
    expect(six).toMatchObject({ score: 6, passed: false, passScore: UNIT_TEST_PASS });
    expect(six.results.every((r) => r.solution.length > 0)).toBe(true);
    await expect(submitUnitTest(deps(), f.userId, first.attemptId, answersFor(10, first.questions))).rejects.toMatchObject({ code: "already_submitted" });
    expect(await unitTestStatus(f.h.db, f.store, f.userId, UNIT)).toMatchObject({ attempts: 1, bestScore: 6, passed: false });

    const second = await startUnitTest(f.h.db, f.store, f.userId, UNIT, new Date(NOW.getTime() + 3_600_000));
    expect(second.attemptId).not.toBe(first.attemptId);
    const firstSet = new Set(first.questions.map((q) => q.exerciseId));
    expect(second.questions.filter((q) => firstSet.has(q.exerciseId)).length).toBe(0);
    const seven = await submitUnitTest(deps(), f.userId, second.attemptId, answersFor(7, second.questions), NOW);
    expect(seven).toMatchObject({ score: 7, passed: true });
    expect(await unitTestStatus(f.h.db, f.store, f.userId, UNIT)).toMatchObject({ attempts: 2, bestScore: 7, passed: true });
  });

  it("empty or missing answers count as wrong and the wrong number of answers is refused", async () => {
    const [u] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "Blank" }).returning();
    const a = await startUnitTest(f.h.db, f.store, u!.id, UNIT, NOW);
    await expect(submitUnitTest(deps(), u!.id, a.attemptId, ["1"])).rejects.toMatchObject({ code: "invalid_answers" });
    const r = await submitUnitTest(deps(), u!.id, a.attemptId, a.questions.map(() => ""), NOW);
    expect(r).toMatchObject({ score: 0, passed: false });
  });
});

describe("the unit counts as complete only when the test is passed", () => {
  it("all lessons done gives 80% of the unit; passing the test gives 100%", async () => {
    const [u] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "Finisher" }).returning();
    const userId = u!.id;
    for (const lessonId of ["geo-m01-u01-l01", "geo-m01-u01-l02", "geo-m01-u01-l03", "geo-m01-u01-l04"]) {
      const lesson = f.store.lesson(lessonId)!.lesson;
      const ids = [...lesson.sections.map((s) => s.id), ...allExercises(lesson).map((e) => e.id)];
      for (const id of ids) await f.h.db.insert(schema.sectionProgress).values({ userId, lessonId, sectionId: dbSectionId(lessonId, id), completedAt: NOW }).onConflictDoNothing();
    }
    await refreshProgress(f.h.db, f.store, userId, NOW);
    const before = (await readProgress(f.h.db, userId, [{ kind: "unit", id: UNIT }])).get(`unit:${UNIT}`)!;
    expect(before.exact).toBe("4/5");
    expect(before.percent).toBe(80);

    const attempt = await startUnitTest(f.h.db, f.store, userId, UNIT, NOW);
    const res = await submitUnitTest(deps(), userId, attempt.attemptId, attempt.questions.map(keyOf), NOW);
    expect(res).toMatchObject({ score: 10, passed: true });
    await refreshProgress(f.h.db, f.store, userId, NOW);
    const after = (await readProgress(f.h.db, userId, [{ kind: "unit", id: UNIT }])).get(`unit:${UNIT}`)!;
    expect(after.exact).toBe("1");

    const dash = await getDashboard(f.h.db, f.store, userId, "geo");
    const unit = dash.courses[0]!.modules[0]!.units.find((x) => x.id === UNIT)!;
    expect(unit.test).toMatchObject({ exists: true, passed: true, bestScore: 10 });
  });
});
