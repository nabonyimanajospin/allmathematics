/**
 * Progress formulas (spec section 9.2). Pure functions, exact arithmetic, no I/O.
 * The server is the only place these are evaluated; the browser only displays the result
 * (and may predict it optimistically with the same functions).
 */

import { add, frac, ONE, ZERO, mul, div, min, type Frac } from "./rational";

export const LESSON_WEIGHTS = { sections: 40, practice: 20, quiz: 40 } as const;
export const MODULE_WEIGHTS = { units: 80, test: 20 } as const;

export interface LessonInputs {
  sectionsCompleted: number;
  sectionsTotal: number;
  /** Distinct exercises of the lesson solved correctly. */
  practiceSolved: number;
  /** All exercises of the lesson. Every one must be solved for the practice part to be complete. */
  practiceTotal: number;
  quizPassed: boolean;
  /**
   * Components that exist for this lesson. Before Phase 2 a lesson has no practice set or quiz yet;
   * the missing components' weights are then removed from the total, so a fully read lesson is 100%.
   */
  hasPractice: boolean;
  hasQuiz: boolean;
}

function checkCount(name: string, v: number): void {
  if (!Number.isInteger(v) || v < 0) throw new RangeError(`${name} must be a non-negative integer`);
}

/**
 *   P_lesson = 0.40 * sections/total + 0.20 * exercises solved/exercises total + 0.40 * [quiz passed]
 * normalised over the components the lesson actually has. A lesson reaches 100% only when every section
 * is completed and every exercise is solved correctly.
 */
export function lessonProgress(i: LessonInputs): Frac {
  checkCount("sectionsCompleted", i.sectionsCompleted);
  checkCount("sectionsTotal", i.sectionsTotal);
  checkCount("practiceSolved", i.practiceSolved);
  checkCount("practiceTotal", i.practiceTotal);
  if (i.practiceSolved > i.practiceTotal) throw new RangeError("practiceSolved exceeds practiceTotal");
  if (i.hasPractice && i.practiceTotal === 0) throw new RangeError("a lesson with practice needs at least one exercise");
  if (i.sectionsCompleted > i.sectionsTotal) throw new RangeError("sectionsCompleted exceeds sectionsTotal");

  let weight = LESSON_WEIGHTS.sections;
  let total: Frac =
    i.sectionsTotal === 0
      ? ZERO
      : mul(frac(LESSON_WEIGHTS.sections), frac(i.sectionsCompleted, i.sectionsTotal));

  if (i.hasPractice) {
    weight += LESSON_WEIGHTS.practice;
    total = add(total, mul(frac(LESSON_WEIGHTS.practice), frac(i.practiceSolved, i.practiceTotal)));
  }
  if (i.hasQuiz) {
    weight += LESSON_WEIGHTS.quiz;
    if (i.quizPassed) total = add(total, frac(LESSON_WEIGHTS.quiz));
  }
  return div(total, frac(weight));
}

export interface Weighted {
  /** Estimated minutes (a positive integer). */
  weight: number;
  progress: Frac;
}

/** Time-weighted average. Empty or zero-weight input gives 0. */
export function weightedAverage(items: readonly Weighted[]): Frac {
  let sumW = ZERO;
  let sumWP = ZERO;
  for (const it of items) {
    checkCount("weight", it.weight);
    const w = frac(it.weight);
    sumW = add(sumW, w);
    sumWP = add(sumWP, mul(w, it.progress));
  }
  if (sumW.num === 0n) return ZERO;
  return min(ONE, div(sumWP, sumW));
}

/** Unit progress = time-weighted average of its lessons. */
export const unitProgress = weightedAverage;

/**
 *   P_module = 0.80 * weighted average of unit progress + 0.20 * [module test passed]
 * If the module has no test yet, the test weight is removed.
 */
export function moduleProgress(units: readonly Weighted[], test: { exists: boolean; passed: boolean }): Frac {
  const avg = weightedAverage(units);
  if (!test.exists) return avg;
  const total = add(mul(frac(MODULE_WEIGHTS.units), avg), test.passed ? frac(MODULE_WEIGHTS.test) : ZERO);
  return div(total, frac(MODULE_WEIGHTS.units + MODULE_WEIGHTS.test));
}

/** Course progress = time-weighted average of module progress. */
export const courseProgress = weightedAverage;

/** Minimum active seconds on a section before scrolling through it counts as completed. */
export const DEFAULT_MIN_SECONDS: Readonly<Record<string, number>> = {
  concept: 20,
  definition: 15,
  theorem: 20,
  formula: 10,
  example: 20,
  visual: 15,
  summary: 10,
};
