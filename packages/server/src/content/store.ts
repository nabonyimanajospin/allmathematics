/**
 * In-memory index of the content tree, loaded from the /content folder. Services use it to know the
 * structure (which section belongs to which lesson, unit, module) and, server-side only, the answer keys.
 */

import { readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import {
  loadContentOrThrow,
  type CourseNode,
  type Lesson,
  type ModuleNode,
  type UnitNode,
} from "@allmaths/content-schema";

export interface LessonRef {
  lesson: Lesson;
  course: CourseNode;
  module: ModuleNode;
  unit: UnitNode;
}

export interface ContentStore {
  courses: readonly CourseNode[];
  lesson(id: string): LessonRef | undefined;
  /** Section ids as stored in the database: `<lessonId>-<sectionId>`. */
  dbSectionId(lessonId: string, sectionId: string): string;
}

export function dbSectionId(lessonId: string, sectionId: string): string {
  return `${lessonId}-${sectionId}`;
}

export function buildStore(courses: readonly CourseNode[]): ContentStore {
  const byId = new Map<string, LessonRef>();
  for (const course of courses)
    for (const module of course.modules)
      for (const unit of module.units)
        for (const l of unit.lessons) byId.set(l.meta.id, { lesson: l.meta, course, module, unit });
  return { courses, lesson: (id) => byId.get(id), dbSectionId };
}

export function loadStore(contentDir: string): ContentStore {
  return buildStore(loadContentOrThrow(contentDir).courses);
}

function newestMtime(dir: string): number {
  let newest = 0;
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    newest = Math.max(newest, st.isDirectory() ? newestMtime(p) : st.mtimeMs);
  }
  return newest;
}

/** A store that reloads when a content file changes (development) or never (production). */
export function createReloadingStore(contentDir: string, watch: boolean): () => ContentStore {
  let store = loadStore(contentDir);
  let stamp = watch ? newestMtime(contentDir) : 0;
  let checkedAt = Date.now();
  return () => {
    if (watch && Date.now() - checkedAt > 1500) {
      checkedAt = Date.now();
      const m = newestMtime(contentDir);
      if (m !== stamp) {
        try {
          store = loadStore(contentDir);
          stamp = m;
        } catch (e) {
          // keep serving the last valid content; the author sees the error in the dev console
          console.error(String(e));
          stamp = m;
        }
      }
    }
    return store;
  };
}
