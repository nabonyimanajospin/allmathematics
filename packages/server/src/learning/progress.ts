/**
 * Server-side progress (spec section 9.2). Percentages are computed here from stored facts
 * (completed sections, passed quizzes) and never accepted from the browser.
 */

import { and, eq, inArray, sql } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import {
  courseProgress,
  lessonProgress,
  moduleProgress,
  rational,
  unitProgressWithTest,
  type Frac,
  type Weighted,
} from "@allmaths/core";
import { allExercises } from "@allmaths/content-schema";
import type { ContentStore, LessonRef } from "../content/store";
import { dbSectionId } from "../content/store";
import { hasUnitTest, passedUnitIds } from "./unit-test";

export type ProgressKind = "lesson" | "unit" | "module" | "course";

export interface ProgressValue {
  /** Exact value as "num/den" (or "0", "1"). */
  exact: string;
  /** Whole percentage, rounded down; 100 only when exactly complete. */
  percent: number;
  /** Percentage with one decimal, rounded down (so small real progress is not shown as 0). */
  tenths: number;
}

export interface ProgressSnapshot {
  lesson: ProgressValue;
  unit: ProgressValue;
  module: ProgressValue;
  course: ProgressValue;
}

const toValue = (f: Frac): ProgressValue => ({ exact: rational.toString(f), percent: rational.percentFloor(f), tenths: Number((f.num * 1000n) / f.den) / 10 });

async function upsert(db: AppDb, userId: string, kind: ProgressKind, id: string, f: Frac, now: Date): Promise<void> {
  const row = { userId, objectType: kind, objectId: id, num: f.num, den: f.den, percent: rational.percentFloor(f), updatedAt: now };
  await db
    .insert(schema.progress)
    .values(row)
    .onConflictDoUpdate({
      target: [schema.progress.userId, schema.progress.objectType, schema.progress.objectId],
      set: { num: row.num, den: row.den, percent: row.percent, updatedAt: now },
    });
}

/** Lesson progress from stored section completion. */
export async function computeLessonFrac(db: AppDb, userId: string, ref: LessonRef): Promise<Frac> {
  const rows = await db
    .select({ sectionId: schema.sectionProgress.sectionId })
    .from(schema.sectionProgress)
    .where(
      and(
        eq(schema.sectionProgress.userId, userId),
        eq(schema.sectionProgress.lessonId, ref.lesson.id),
        sql`${schema.sectionProgress.completedAt} is not null`,
      ),
    );
  const valid = new Set(ref.lesson.sections.map((s) => dbSectionId(ref.lesson.id, s.id)));
  const exercises = new Set(allExercises(ref.lesson).map((e) => dbSectionId(ref.lesson.id, e.id)));
  const completed = rows.filter((r) => valid.has(r.sectionId)).length;
  const solved = rows.filter((r) => exercises.has(r.sectionId)).length;
  return lessonProgress({
    sectionsCompleted: completed,
    sectionsTotal: ref.lesson.sections.length,
    practiceSolved: solved,
    practiceTotal: exercises.size,
    quizPassed: false,
    hasPractice: exercises.size > 0,
    hasQuiz: false,
  });
}

/** Recompute and store lesson, unit, module and course progress after something changed in a lesson, and return the values of its chain. */
export async function recomputeProgress(
  db: AppDb,
  store: ContentStore,
  userId: string,
  lessonId: string,
  now = new Date(),
): Promise<ProgressSnapshot> {
  const ref = store.lesson(lessonId);
  if (!ref) throw new Error(`Unknown lesson ${lessonId}`);
  await refreshProgress(db, store, userId, now);
  const p = await readProgress(db, userId, [
    { kind: "lesson", id: lessonId },
    { kind: "unit", id: ref.unit.meta.id },
    { kind: "module", id: ref.module.meta.id },
    { kind: "course", id: ref.course.meta.id },
  ]);
  const get = (k: string): ProgressValue => p.get(k) ?? toValue(rational.ZERO);
  return { lesson: get(`lesson:${lessonId}`), unit: get(`unit:${ref.unit.meta.id}`), module: get(`module:${ref.module.meta.id}`), course: get(`course:${ref.course.meta.id}`) };
}

/** Stored progress for display. Missing rows mean 0. */
export async function readProgress(
  db: AppDb,
  userId: string,
  items: { kind: ProgressKind; id: string }[],
): Promise<Map<string, ProgressValue>> {
  const out = new Map<string, ProgressValue>();
  if (items.length === 0) return out;
  const rows = await db
    .select()
    .from(schema.progress)
    .where(and(eq(schema.progress.userId, userId), inArray(schema.progress.objectId, items.map((i) => i.id))));
  for (const r of rows) out.set(`${r.objectType}:${r.objectId}`, toValue(rational.frac(r.num, r.den)));
  for (const i of items) if (!out.has(`${i.kind}:${i.id}`)) out.set(`${i.kind}:${i.id}`, toValue(rational.ZERO));
  return out;
}


/**
 * Recomputes lesson, unit, module and course progress of one learner from what they actually did (completed sections and
 * solved exercises) against the current content, and stores the values that differ. Content changes (a new exercise, a new lesson)
 * therefore never leave an old percentage on the screen.
 */
export async function refreshProgress(db: AppDb, store: ContentStore, userId: string, now = new Date()): Promise<void> {
  const done = new Set(
    (
      await db
        .select({ sectionId: schema.sectionProgress.sectionId })
        .from(schema.sectionProgress)
        .where(and(eq(schema.sectionProgress.userId, userId), sql`${schema.sectionProgress.completedAt} is not null`))
    ).map((r) => r.sectionId),
  );
  const passedUnits = await passedUnitIds(db, userId);
  const target = new Map<string, Frac>();
  const lessonFrac = (id: string): Frac => {
    const ref = store.lesson(id);
    if (!ref) return rational.ZERO;
    const exercises = allExercises(ref.lesson);
    const sections = ref.lesson.sections.filter((x) => done.has(dbSectionId(id, x.id))).length;
    const solved = exercises.filter((e) => done.has(dbSectionId(id, e.id))).length;
    return lessonProgress({
      sectionsCompleted: sections,
      sectionsTotal: ref.lesson.sections.length,
      practiceSolved: solved,
      practiceTotal: exercises.length,
      quizPassed: false,
      hasPractice: exercises.length > 0,
      hasQuiz: false,
    });
  };
  for (const course of store.courses) {
    const moduleItems: Weighted[] = [];
    for (const m of course.modules) {
      const unitItems: Weighted[] = [];
      for (const u of m.units) {
        const items: Weighted[] = u.lessons.map((l) => {
          const f = lessonFrac(l.meta.id);
          target.set(`lesson:${l.meta.id}`, f);
          return { weight: l.meta.estMinutes, progress: f };
        });
        const uf = unitProgressWithTest(items, { exists: hasUnitTest(store, u.meta.id), passed: passedUnits.has(u.meta.id) });
        target.set(`unit:${u.meta.id}`, uf);
        unitItems.push({ weight: u.lessons.reduce((a, l) => a + l.meta.estMinutes, 0), progress: uf });
      }
      const mf = moduleProgress(unitItems, { exists: false, passed: false });
      target.set(`module:${m.meta.id}`, mf);
      moduleItems.push({ weight: m.units.reduce((a, u) => a + u.lessons.reduce((b, l) => b + l.meta.estMinutes, 0), 0), progress: mf });
    }
    target.set(`course:${course.meta.id}`, courseProgress(moduleItems));
  }
  const stored = new Map<string, Frac>();
  for (const r of await db.select().from(schema.progress).where(eq(schema.progress.userId, userId))) stored.set(`${r.objectType}:${r.objectId}`, rational.frac(r.num, r.den));
  for (const [key, f] of target) {
    const old = stored.get(key);
    if (old ? rational.eq(old, f) : f.num === 0n) continue;
    const [kind, ...rest] = key.split(":");
    await upsert(db, userId, kind as ProgressKind, rest.join(":"), f, now);
  }
}
