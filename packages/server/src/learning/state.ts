/** Read models for the lesson player and the dashboard. */

import { and, desc, eq } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import type { ContentStore } from "../content/store";
import { dbSectionId } from "../content/store";
import { readProgress, type ProgressValue, type ProgressSnapshot } from "./progress";

export interface LessonState {
  lessonId: string;
  sectionsTotal: number;
  /** Content section ids (not database ids) that are complete. */
  completedSectionIds: string[];
  hintsUsed: Record<string, number>;
  /** Section to open: the one the student touched last ("resume where I left off"). */
  resumeSectionId: string;
  /** First section that is not complete yet, or null when the lesson is finished. */
  nextIncompleteSectionId: string | null;
  progress: ProgressSnapshot;
}

export async function getLessonState(db: AppDb, store: ContentStore, userId: string, lessonId: string): Promise<LessonState | null> {
  const ref = store.lesson(lessonId);
  if (!ref) return null;
  const rows = await db
    .select()
    .from(schema.sectionProgress)
    .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.lessonId, lessonId)))
    .orderBy(desc(schema.sectionProgress.updatedAt));

  const prefix = `${lessonId}-`;
  const contentIds = new Set(ref.lesson.sections.map((s) => s.id));
  const toContentId = (dbId: string): string => (dbId.startsWith(prefix) ? dbId.slice(prefix.length) : dbId);

  const completed = new Set<string>();
  const hints: Record<string, number> = {};
  for (const r of rows) {
    const id = toContentId(r.sectionId);
    if (!contentIds.has(id)) continue;
    if (r.completedAt) completed.add(id);
    if (r.hintsUsed > 0) hints[id] = r.hintsUsed;
  }
  const firstIncomplete = ref.lesson.sections.find((s) => !completed.has(s.id))?.id ?? null;
  const lastTouched = rows.map((r) => toContentId(r.sectionId)).find((id) => contentIds.has(id));
  const first = ref.lesson.sections[0]?.id ?? "";
  // Resume at the section last touched; if that one is done, continue at the next unfinished one.
  const resume = lastTouched && !completed.has(lastTouched) ? lastTouched : (firstIncomplete ?? lastTouched ?? first);

  const p = await readProgress(db, userId, [
    { kind: "lesson", id: lessonId },
    { kind: "unit", id: ref.unit.meta.id },
    { kind: "module", id: ref.module.meta.id },
    { kind: "course", id: ref.course.meta.id },
  ]);
  const get = (k: string): ProgressValue => p.get(k) ?? { exact: "0", percent: 0 };
  return {
    lessonId,
    sectionsTotal: ref.lesson.sections.length,
    completedSectionIds: ref.lesson.sections.filter((s) => completed.has(s.id)).map((s) => s.id),
    hintsUsed: hints,
    resumeSectionId: resume,
    nextIncompleteSectionId: firstIncomplete,
    progress: {
      lesson: get(`lesson:${lessonId}`),
      unit: get(`unit:${ref.unit.meta.id}`),
      module: get(`module:${ref.module.meta.id}`),
      course: get(`course:${ref.course.meta.id}`),
    },
  };
}

export interface DashboardLesson {
  id: string;
  title: string;
  estMinutes: number;
  percent: number;
}
export interface DashboardUnit {
  id: string;
  title: string;
  percent: number;
  lessons: DashboardLesson[];
}
export interface DashboardModule {
  id: string;
  title: string;
  free: boolean;
  percent: number;
  units: DashboardUnit[];
}
export interface DashboardCourse {
  id: string;
  title: string;
  description: string;
  percent: number;
  modules: DashboardModule[];
}
export interface Dashboard {
  courses: DashboardCourse[];
  /** The lesson to continue: started but unfinished first, else the first untouched one. */
  continueLessonId: string | null;
}

export async function getDashboard(db: AppDb, store: ContentStore, userId: string): Promise<Dashboard> {
  const items: { kind: "lesson" | "unit" | "module" | "course"; id: string }[] = [];
  for (const c of store.courses) {
    items.push({ kind: "course", id: c.meta.id });
    for (const m of c.modules) {
      items.push({ kind: "module", id: m.meta.id });
      for (const u of m.units) {
        items.push({ kind: "unit", id: u.meta.id });
        for (const l of u.lessons) items.push({ kind: "lesson", id: l.meta.id });
      }
    }
  }
  const p = await readProgress(db, userId, items);
  const pct = (kind: string, id: string): number => p.get(`${kind}:${id}`)?.percent ?? 0;

  let inProgress: string | null = null;
  let firstUntouched: string | null = null;
  const courses: DashboardCourse[] = store.courses.map((c) => ({
    id: c.meta.id,
    title: c.meta.title,
    description: c.meta.description,
    percent: pct("course", c.meta.id),
    modules: c.modules.map((m) => ({
      id: m.meta.id,
      title: m.meta.title,
      free: m.meta.free,
      percent: pct("module", m.meta.id),
      units: m.units.map((u) => ({
        id: u.meta.id,
        title: u.meta.title,
        percent: pct("unit", u.meta.id),
        lessons: u.lessons.map((l) => {
          const percent = pct("lesson", l.meta.id);
          if (percent > 0 && percent < 100) inProgress ??= l.meta.id;
          if (percent === 0) firstUntouched ??= l.meta.id;
          return { id: l.meta.id, title: l.meta.title, estMinutes: l.meta.estMinutes, percent };
        }),
      })),
    })),
  }));
  return { courses, continueLessonId: inProgress ?? firstUntouched };
}

/** Database id helper re-exported for callers that map between content and database ids. */
export { dbSectionId };
