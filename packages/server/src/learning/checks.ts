/**
 * Check questions inside lessons: answer checking, progressive hints and explanations.
 * The answer key is read from the server-side content and never leaves this module (spec section 13).
 */

import { randomUUID } from "node:crypto";
import { and, eq } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import { EngineUnavailableError, type EngineClient } from "@allmaths/core";
import { toEngineRequest, type CheckSpec } from "@allmaths/content-schema";
import type { ContentStore } from "../content/store";
import { dbSectionId } from "../content/store";
import { AppError, Errors } from "../errors";
import { recomputeProgress, type ProgressSnapshot } from "./progress";

export interface CheckDeps {
  db: AppDb;
  store: ContentStore;
  engine: Pick<EngineClient, "check">;
}

export interface CheckOutcome {
  status: "correct" | "incorrect" | "invalid";
  code: string;
  message: string;
  /** Specific feedback for a recognised common mistake. */
  hint?: string;
  /** The student's answer as the engine understood it, in LaTeX. */
  studentLatex?: string;
  parts?: boolean[];
  /** Only present after a correct answer. */
  explanation?: string;
  progress?: ProgressSnapshot;
}

/** A check inside the lesson, or an exercise of one of its exercise sets: both are questions with a key. */
interface Question extends CheckSpec {
  /** Shown after a correct answer or on request: the explanation of a check, the solution of an exercise. */
  explanation: string;
  allowDecimal?: boolean | undefined;
}

function findCheck(store: ContentStore, lessonId: string, sectionId: string): { check: Question; sectionDb: string } {
  const ref = store.lesson(lessonId);
  if (!ref) throw Errors.notFound("Question not found");
  const s = ref.lesson.sections.find((x) => x.id === sectionId);
  if (s && s.type === "check") return { check: s, sectionDb: dbSectionId(lessonId, sectionId) };
  for (const set of ref.lesson.exerciseSets) {
    const item = set.items.find((x) => x.id === sectionId);
    if (item) return { check: { ...item, explanation: item.solution }, sectionDb: dbSectionId(lessonId, sectionId) };
  }
  throw Errors.notFound("Question not found");
}

async function ensureRow(db: AppDb, userId: string, lessonId: string, sectionDb: string, now: Date): Promise<void> {
  await db
    .insert(schema.sectionProgress)
    .values({ userId, lessonId, sectionId: sectionDb, updatedAt: now })
    .onConflictDoNothing();
}

export async function checkAnswer(
  deps: CheckDeps,
  userId: string,
  lessonId: string,
  sectionId: string,
  answer: string,
  now = new Date(),
): Promise<CheckOutcome> {
  const { db, store, engine } = deps;
  const { check, sectionDb } = findCheck(store, lessonId, sectionId);
  if (answer.length === 0 || answer.length > 400) throw Errors.badRequest("The answer is empty or too long.", "invalid_answer");

  let res;
  try {
    res = await engine.check(toEngineRequest(check, answer));
  } catch (e) {
    if (e instanceof EngineUnavailableError) throw Errors.unavailable("Answer checking is temporarily unavailable. Please try again.", e);
    throw e;
  }

  const outcome: CheckOutcome = { status: res.status, code: res.code, message: res.message };
  if (res.hint) outcome.hint = res.hint;
  if (res.student_latex) outcome.studentLatex = res.student_latex;
  if (res.parts) outcome.parts = res.parts;

  // 'invalid' means "not a usable answer": nothing is recorded and no attempt is counted.
  if (res.status === "invalid") return outcome;

  await db.transaction(async (tx) => {
    await tx.insert(schema.events).values({
      id: randomUUID(),
      userId,
      verb: "answered",
      objectType: "section",
      objectId: sectionDb,
      lessonId,
      sectionId: sectionDb,
      resultJson: { correct: res.status === "correct", answerLatex: res.student_latex ?? answer.slice(0, 200) },
      ts: now,
    });
    await ensureRow(tx, userId, lessonId, sectionDb, now);
    if (res.status === "correct") {
      await tx
        .update(schema.sectionProgress)
        .set({ checkAnsweredCorrectly: true, completedAt: now, updatedAt: now })
        .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.sectionId, sectionDb)));
    } else {
      await tx
        .update(schema.sectionProgress)
        .set({ updatedAt: now })
        .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.sectionId, sectionDb)));
    }
  });

  if (res.status === "correct") {
    outcome.explanation = check.explanation;
    outcome.progress = await recomputeProgress(db, store, userId, lessonId, now);
  }
  return outcome;
}

/** Reveals hints one at a time, in order. Using a hint is recorded (it reduces points in Phase 2). */
export async function getHint(
  deps: Pick<CheckDeps, "db" | "store">,
  userId: string,
  lessonId: string,
  sectionId: string,
  index: number,
  now = new Date(),
): Promise<{ text: string; hintsUsed: number; hintCount: number }> {
  const { db, store } = deps;
  const { check, sectionDb } = findCheck(store, lessonId, sectionId);
  if (!Number.isInteger(index) || index < 0 || index >= check.hints.length) throw Errors.badRequest("There is no such hint.", "no_such_hint");

  await ensureRow(db, userId, lessonId, sectionDb, now);
  const [row] = await db
    .select({ hintsUsed: schema.sectionProgress.hintsUsed })
    .from(schema.sectionProgress)
    .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.sectionId, sectionDb)));
  const used = row?.hintsUsed ?? 0;
  if (index > used) throw new AppError("hint_locked", 400, "Use the previous hint first.");

  if (index === used) {
    await db.transaction(async (tx) => {
      await tx
        .update(schema.sectionProgress)
        .set({ hintsUsed: used + 1, updatedAt: now })
        .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.sectionId, sectionDb)));
      await tx.insert(schema.events).values({
        id: randomUUID(), userId, verb: "hinted", objectType: "section", objectId: sectionDb, lessonId, sectionId: sectionDb,
        resultJson: { hint: index + 1 }, ts: now,
      });
    });
  }
  const text = check.hints[index];
  if (text === undefined) throw Errors.badRequest("There is no such hint.", "no_such_hint");
  return { text, hintsUsed: Math.max(used, index + 1), hintCount: check.hints.length };
}

/** Shows the worked explanation (after giving up). It does not complete the question. */
export async function revealSolution(
  deps: Pick<CheckDeps, "db" | "store">,
  userId: string,
  lessonId: string,
  sectionId: string,
  now = new Date(),
): Promise<{ explanation: string }> {
  const { db, store } = deps;
  const { check, sectionDb } = findCheck(store, lessonId, sectionId);
  await db.insert(schema.events).values({
    id: randomUUID(), userId, verb: "revealed_solution", objectType: "section", objectId: sectionDb, lessonId, sectionId: sectionDb, ts: now,
  });
  return { explanation: check.explanation };
}
