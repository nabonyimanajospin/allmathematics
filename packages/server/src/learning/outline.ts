/** The outline of a course for the side panel of a lesson: modules, units and lessons with the student's progress. */

import type { AppDb } from "@allmaths/db";
import type { ContentStore } from "../content/store";
import { readProgress, refreshProgress } from "./progress";
import { unitTestStatuses, type UnitTestStatus } from "./unit-test";

export interface OutlineLesson {
  id: string;
  title: string;
  estMinutes: number;
  percent: number;
  current: boolean;
}

export interface OutlineUnit {
  id: string;
  title: string;
  lessons: OutlineLesson[];
  /** The test at the end of the unit (null when the unit has none yet) and the learner's record. */
  test: UnitTestStatus | null;
}

export interface OutlineModule {
  id: string;
  title: string;
  percent: number;
  /** The module that contains the lesson being read. */
  current: boolean;
  units: OutlineUnit[];
}

export interface CourseOutline {
  courseId: string;
  title: string;
  percent: number;
  modules: OutlineModule[];
}

export async function getCourseOutline(db: AppDb, store: ContentStore, userId: string, lessonId: string): Promise<CourseOutline | null> {
  const ref = store.lesson(lessonId);
  if (!ref) return null;
  const course = ref.course;
  const items = [
    { kind: "course" as const, id: course.meta.id },
    ...course.modules.flatMap((m) => [
      { kind: "module" as const, id: m.meta.id },
      ...m.units.flatMap((u) => u.lessons.map((l) => ({ kind: "lesson" as const, id: l.meta.id }))),
    ]),
  ];
  await refreshProgress(db, store, userId);
  const progress = await readProgress(db, userId, items);
  const tests = await unitTestStatuses(db, store, userId);
  const pct = (kind: string, id: string): number => progress.get(`${kind}:${id}`)?.percent ?? 0;
  return {
    courseId: course.meta.id,
    title: course.meta.title,
    percent: pct("course", course.meta.id),
    modules: course.modules.map((m) => ({
      id: m.meta.id,
      title: m.meta.title,
      percent: pct("module", m.meta.id),
      current: m.meta.id === ref.module.meta.id,
      units: m.units.map((u) => ({
        id: u.meta.id,
        title: u.meta.title,
        test: tests.get(u.meta.id)?.exists ? (tests.get(u.meta.id) ?? null) : null,
        lessons: u.lessons.map((l) => ({
          id: l.meta.id,
          title: l.meta.title,
          estMinutes: l.meta.estMinutes,
          percent: pct("lesson", l.meta.id),
          current: l.meta.id === lessonId,
        })),
      })),
    })),
  };
}
