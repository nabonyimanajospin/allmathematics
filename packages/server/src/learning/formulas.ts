/** The student's formula sheet: formulas and theorems saved from the lessons. */

import { and, eq } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import type { ContentStore } from "../content/store";
import { dbSectionId } from "../content/store";
import { Errors } from "../errors";

export interface SavedFormula {
  lessonId: string;
  lessonTitle: string;
  courseId: string;
  courseTitle: string;
  moduleTitle: string;
  sectionId: string;
  kind: "formula" | "theorem";
}

const SAVEABLE = new Set(["formula", "theorem"]);

/** The sections of a lesson that were saved, as content ids. */
export async function savedSectionIds(db: AppDb, store: ContentStore, userId: string, lessonId: string): Promise<string[]> {
  const ref = store.lesson(lessonId);
  if (!ref) return [];
  const rows = await db.select().from(schema.bookmarks).where(eq(schema.bookmarks.userId, userId));
  const saved = new Set(rows.map((r) => r.sectionId));
  return ref.lesson.sections.filter((s) => SAVEABLE.has(s.type) && saved.has(dbSectionId(lessonId, s.id))).map((s) => s.id);
}

/** Every saved formula of the user, in the order of the curriculum. */
export async function listFormulas(db: AppDb, store: ContentStore, userId: string): Promise<SavedFormula[]> {
  const rows = await db.select().from(schema.bookmarks).where(eq(schema.bookmarks.userId, userId));
  const saved = new Set(rows.map((r) => r.sectionId));
  const out: SavedFormula[] = [];
  for (const course of store.courses)
    for (const module of course.modules)
      for (const unit of module.units)
        for (const l of unit.lessons)
          for (const s of l.meta.sections) {
            if (!SAVEABLE.has(s.type) || !saved.has(dbSectionId(l.meta.id, s.id))) continue;
            out.push({
              lessonId: l.meta.id,
              lessonTitle: l.meta.title,
              courseId: course.meta.id,
              courseTitle: course.meta.title,
              moduleTitle: module.meta.title,
              sectionId: s.id,
              kind: s.type as "formula" | "theorem",
            });
          }
  return out;
}

/** Save or remove one formula. Only a formula or a theorem of a real lesson can be saved. */
export async function setFormulaSaved(db: AppDb, store: ContentStore, userId: string, lessonId: string, sectionId: string, saved: boolean): Promise<void> {
  const ref = store.lesson(lessonId);
  const section = ref?.lesson.sections.find((s) => s.id === sectionId);
  if (!ref || !section || !SAVEABLE.has(section.type)) throw Errors.notFound();
  const id = dbSectionId(lessonId, sectionId);
  if (saved) await db.insert(schema.bookmarks).values({ userId, sectionId: id }).onConflictDoNothing();
  else await db.delete(schema.bookmarks).where(and(eq(schema.bookmarks.userId, userId), eq(schema.bookmarks.sectionId, id)));
}
