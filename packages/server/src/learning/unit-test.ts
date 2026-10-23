/**
 * The test at the end of every unit: 10 questions where the student types the answer (no multiple choice), drawn from the exercises
 * of the unit's lessons and checked by the math engine. 7 correct answers pass. A new attempt draws different questions, and the unit
 * counts as 100% only when the test is passed. The answers are never sent to the browser before the attempt is submitted.
 */

import { randomInt } from "node:crypto";
import { and, desc, eq, isNull } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import { EngineUnavailableError, type EngineClient } from "@allmaths/core";
import { allExercises, toEngineRequest, type Exercise } from "@allmaths/content-schema";
import type { ContentStore } from "../content/store";
import { AppError, Errors } from "../errors";

export const UNIT_TEST_QUESTIONS = 10;
export const UNIT_TEST_PASS = 7;
/** A started attempt that is not submitted within this time is abandoned. */
export const ATTEMPT_HOURS = 3;

export interface TestQuestionRef {
  lessonId: string;
  exerciseId: string;
}

export interface UnitTestStatus {
  exists: boolean;
  attempts: number;
  bestScore: number | null;
  passed: boolean;
}

/** The exercises a test may use: typed answers only, from the lessons of the unit. */
export function unitTestBank(store: ContentStore, unitId: string): TestQuestionRef[] {
  const out: TestQuestionRef[] = [];
  for (const course of store.courses)
    for (const m of course.modules)
      for (const u of m.units) {
        if (u.meta.id !== unitId) continue;
        for (const l of u.lessons) {
          const lesson = store.lesson(l.meta.id)?.lesson;
          if (!lesson) continue;
          for (const e of allExercises(lesson)) if (e.answerType !== "multiple_choice") out.push({ lessonId: l.meta.id, exerciseId: e.id });
        }
      }
  return out;
}

/** A unit has a test when its bank can fill one. */
export function hasUnitTest(store: ContentStore, unitId: string): boolean {
  return unitTestBank(store, unitId).length >= UNIT_TEST_QUESTIONS;
}

/** The unit that contains a lesson. */
export function unitOfLesson(store: ContentStore, lessonId: string): string | null {
  return store.lesson(lessonId)?.unit.meta.id ?? null;
}

function shuffle<T>(items: T[], rnd: (n: number) => number): T[] {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = rnd(i + 1);
    [a[i], a[j]] = [a[j]!, a[i]!];
  }
  return a;
}

/**
 * Picks `n` questions spread over the lessons of the unit (round robin over the lessons, each in random order), avoiding the
 * questions of `avoid` as long as the bank is large enough.
 */
export function pickQuestions(bank: TestQuestionRef[], n: number, avoid: TestQuestionRef[] = [], rnd: (n: number) => number = randomInt): TestQuestionRef[] {
  const avoidSet = new Set(avoid.map((q) => `${q.lessonId}/${q.exerciseId}`));
  let pool = bank.filter((q) => !avoidSet.has(`${q.lessonId}/${q.exerciseId}`));
  if (pool.length < n) pool = bank;
  const byLesson = new Map<string, TestQuestionRef[]>();
  for (const q of shuffle(pool, rnd)) byLesson.set(q.lessonId, [...(byLesson.get(q.lessonId) ?? []), q]);
  const lessons = shuffle([...byLesson.keys()], rnd);
  const picked: TestQuestionRef[] = [];
  while (picked.length < n && lessons.some((l) => (byLesson.get(l)?.length ?? 0) > 0)) {
    for (const l of lessons) {
      const next = byLesson.get(l)?.shift();
      if (next && picked.length < n) picked.push(next);
    }
  }
  return shuffle(picked, rnd);
}

function parseQuestions(value: unknown): TestQuestionRef[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((v) => {
    const o = v as Partial<TestQuestionRef>;
    return typeof o.lessonId === "string" && typeof o.exerciseId === "string" ? [{ lessonId: o.lessonId, exerciseId: o.exerciseId }] : [];
  });
}

export function findExercise(store: ContentStore, ref: TestQuestionRef): Exercise | undefined {
  const lesson = store.lesson(ref.lessonId)?.lesson;
  return lesson ? allExercises(lesson).find((e) => e.id === ref.exerciseId) : undefined;
}

export interface OpenAttempt {
  attemptId: string;
  unitId: string;
  questions: TestQuestionRef[];
}

/** Starts a test, or returns the attempt that is still open. */
export async function startUnitTest(db: AppDb, store: ContentStore, userId: string, unitId: string, now = new Date()): Promise<OpenAttempt> {
  const bank = unitTestBank(store, unitId);
  if (bank.length < UNIT_TEST_QUESTIONS) throw Errors.notFound("This unit has no test");
  const rows = await db
    .select()
    .from(schema.unitTestAttempts)
    .where(and(eq(schema.unitTestAttempts.userId, userId), eq(schema.unitTestAttempts.unitId, unitId)))
    .orderBy(desc(schema.unitTestAttempts.startedAt))
    .limit(5);
  const open = rows.find((r) => r.submittedAt === null && now.getTime() - r.startedAt.getTime() < ATTEMPT_HOURS * 3_600_000);
  if (open) return { attemptId: open.id, unitId, questions: parseQuestions(open.questions) };
  const questions = pickQuestions(bank, UNIT_TEST_QUESTIONS, rows[0] ? parseQuestions(rows[0].questions) : []);
  const [row] = await db.insert(schema.unitTestAttempts).values({ userId, unitId, questions, startedAt: now }).returning({ id: schema.unitTestAttempts.id });
  if (!row) throw new Error("insert returned no row");
  return { attemptId: row.id, unitId, questions };
}

/** The questions of an open attempt of this learner. */
export async function getOpenAttempt(db: AppDb, userId: string, attemptId: string): Promise<(OpenAttempt & { submitted: boolean }) | null> {
  const [row] = await db
    .select()
    .from(schema.unitTestAttempts)
    .where(and(eq(schema.unitTestAttempts.id, attemptId), eq(schema.unitTestAttempts.userId, userId)));
  if (!row) return null;
  return { attemptId: row.id, unitId: row.unitId, questions: parseQuestions(row.questions), submitted: row.submittedAt !== null };
}

export interface QuestionResult {
  index: number;
  correct: boolean;
  /** The worked solution, shown only after the attempt is submitted. */
  solution: string;
  message: string;
}

export interface TestResult {
  score: number;
  total: number;
  passScore: number;
  passed: boolean;
  results: QuestionResult[];
}

/** Checks every answer with the math engine, stores the result and tells the learner. */
export async function submitUnitTest(
  deps: { db: AppDb; store: ContentStore; engine: Pick<EngineClient, "check"> },
  userId: string,
  attemptId: string,
  answers: string[],
  now = new Date(),
): Promise<TestResult> {
  const { db, store, engine } = deps;
  const attempt = await getOpenAttempt(db, userId, attemptId);
  if (!attempt) throw Errors.notFound("Test not found");
  if (attempt.submitted) throw new AppError("already_submitted", 409, "This test was already submitted.");
  if (answers.length !== attempt.questions.length) throw Errors.badRequest("Answer every question or leave it empty.", "invalid_answers");
  if (answers.some((a) => a.length > 400)) throw Errors.badRequest("An answer is too long.", "invalid_answers");

  const results: QuestionResult[] = await Promise.all(
    attempt.questions.map(async (q, index) => {
      const ex = findExercise(store, q);
      if (!ex) return { index, correct: false, solution: "", message: "" };
      const answer = (answers[index] ?? "").trim();
      if (answer === "") return { index, correct: false, solution: ex.solution, message: "No answer." };
      try {
        const res = await engine.check(toEngineRequest(ex, answer));
        return { index, correct: res.status === "correct", solution: ex.solution, message: res.message };
      } catch (e) {
        if (e instanceof EngineUnavailableError) throw Errors.unavailable("Answer checking is temporarily unavailable. Your test was not submitted; please try again.", e);
        throw e;
      }
    }),
  );
  const score = results.filter((r) => r.correct).length;
  const passed = score >= UNIT_TEST_PASS;
  const updated = await db
    .update(schema.unitTestAttempts)
    .set({ answers, score, passed, submittedAt: now })
    .where(and(eq(schema.unitTestAttempts.id, attemptId), eq(schema.unitTestAttempts.userId, userId), isNull(schema.unitTestAttempts.submittedAt)))
    .returning({ id: schema.unitTestAttempts.id });
  if (updated.length === 0) throw new AppError("already_submitted", 409, "This test was already submitted.");
  return { score, total: attempt.questions.length, passScore: UNIT_TEST_PASS, passed, results };
}

/** The learner's record for a unit. */
export async function unitTestStatus(db: AppDb, store: ContentStore, userId: string, unitId: string): Promise<UnitTestStatus> {
  const exists = hasUnitTest(store, unitId);
  if (!exists) return { exists: false, attempts: 0, bestScore: null, passed: false };
  const rows = await db
    .select({ score: schema.unitTestAttempts.score, passed: schema.unitTestAttempts.passed, submittedAt: schema.unitTestAttempts.submittedAt })
    .from(schema.unitTestAttempts)
    .where(and(eq(schema.unitTestAttempts.userId, userId), eq(schema.unitTestAttempts.unitId, unitId)));
  const done = rows.filter((r) => r.submittedAt !== null);
  return {
    exists: true,
    attempts: done.length,
    bestScore: done.length === 0 ? null : Math.max(...done.map((r) => r.score ?? 0)),
    passed: done.some((r) => r.passed),
  };
}

/** The ids of the units whose test this learner has passed. */
export async function passedUnitIds(db: AppDb, userId: string): Promise<Set<string>> {
  const rows = await db
    .select({ unitId: schema.unitTestAttempts.unitId })
    .from(schema.unitTestAttempts)
    .where(and(eq(schema.unitTestAttempts.userId, userId), eq(schema.unitTestAttempts.passed, true)));
  return new Set(rows.map((r) => r.unitId));
}

/** The record of the learner for every unit that has a test (one query). */
export async function unitTestStatuses(db: AppDb, store: ContentStore, userId: string): Promise<Map<string, UnitTestStatus>> {
  const rows = await db
    .select({ unitId: schema.unitTestAttempts.unitId, score: schema.unitTestAttempts.score, passed: schema.unitTestAttempts.passed, submittedAt: schema.unitTestAttempts.submittedAt })
    .from(schema.unitTestAttempts)
    .where(eq(schema.unitTestAttempts.userId, userId));
  const out = new Map<string, UnitTestStatus>();
  for (const course of store.courses)
    for (const m of course.modules)
      for (const u of m.units) {
        const exists = hasUnitTest(store, u.meta.id);
        const done = rows.filter((r) => r.unitId === u.meta.id && r.submittedAt !== null);
        out.set(u.meta.id, {
          exists,
          attempts: done.length,
          bestScore: done.length === 0 ? null : Math.max(...done.map((r) => r.score ?? 0)),
          passed: done.some((r) => r.passed),
        });
      }
  return out;
}
