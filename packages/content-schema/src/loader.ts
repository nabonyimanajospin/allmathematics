/**
 * Loads the content tree from /content (Course → Module → Unit → Lesson) and validates every file.
 * Problems are collected as issues (never thrown) so the verification script can report all of them;
 * `loadContentOrThrow` is for runtime use.
 */

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml, YAMLParseError } from "yaml";
import type { z } from "zod";
import {
  courseSchema,
  lessonSchema,
  moduleSchema,
  unitSchema,
  type CourseMeta,
  type Lesson,
  type ModuleMeta,
  type UnitMeta,
} from "./schema";

export interface ContentIssue {
  file: string;
  message: string;
  severity: "error" | "warning";
}

export interface LessonNode {
  meta: Lesson;
  order: number;
  file: string;
}
export interface UnitNode {
  meta: UnitMeta;
  lessons: LessonNode[];
}
export interface ModuleNode {
  meta: ModuleMeta;
  units: UnitNode[];
}
export interface CourseNode {
  meta: CourseMeta;
  modules: ModuleNode[];
}
export interface ContentTree {
  courses: CourseNode[];
  issues: ContentIssue[];
}

function subdirs(dir: string, pattern: RegExp): { name: string; order: number }[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((n) => statSync(join(dir, n)).isDirectory())
    .map((name) => ({ name, m: pattern.exec(name) }))
    .filter((x): x is { name: string; m: RegExpExecArray } => x.m !== null)
    .map(({ name, m }) => ({ name, order: Number(m[1]) }))
    .sort((a, b) => a.order - b.order);
}

function readYaml<S extends z.ZodType>(file: string, schema: S, issues: ContentIssue[]): z.infer<S> | null {
  if (!existsSync(file)) {
    issues.push({ file, message: "File is missing", severity: "error" });
    return null;
  }
  let raw: unknown;
  try {
    raw = parseYaml(readFileSync(file, "utf8"), { prettyErrors: true });
  } catch (e) {
    const msg = e instanceof YAMLParseError ? e.message : String(e);
    issues.push({ file, message: `YAML syntax error: ${msg}`, severity: "error" });
    return null;
  }
  const parsed = schema.safeParse(raw);
  if (!parsed.success) {
    for (const i of parsed.error.issues) {
      issues.push({ file, message: `${i.path.join(".") || "(root)"}: ${i.message}`, severity: "error" });
    }
    return null;
  }
  return parsed.data;
}

const two = (n: number): string => String(n).padStart(2, "0");

export function loadContent(contentDir: string): ContentTree {
  const issues: ContentIssue[] = [];
  const courses: CourseNode[] = [];
  if (!existsSync(contentDir)) {
    issues.push({ file: contentDir, message: "Content directory not found", severity: "error" });
    return { courses, issues };
  }
  const courseDirs = readdirSync(contentDir).filter((n) => statSync(join(contentDir, n)).isDirectory());
  for (const cdir of courseDirs.sort()) {
    const cpath = join(contentDir, cdir);
    const cmeta = readYaml(join(cpath, "course.yaml"), courseSchema, issues);
    if (!cmeta) continue;
    if (cmeta.id !== cdir) {
      issues.push({ file: join(cpath, "course.yaml"), message: `id “${cmeta.id}” must equal the folder name “${cdir}”`, severity: "error" });
    }
    const course: CourseNode = { meta: cmeta, modules: [] };
    for (const m of subdirs(cpath, /^m(\d{2})-/)) {
      const mpath = join(cpath, m.name);
      const mfile = join(mpath, "module.yaml");
      const mmeta = readYaml(mfile, moduleSchema, issues);
      if (!mmeta) continue;
      const expectedModule = `${cmeta.id}-m${two(m.order)}`;
      if (mmeta.id !== expectedModule || mmeta.order !== m.order) {
        issues.push({ file: mfile, message: `id/order must be “${expectedModule}” / ${m.order} to match the folder`, severity: "error" });
      }
      const mod: ModuleNode = { meta: mmeta, units: [] };
      for (const u of subdirs(mpath, /^u(\d{2})-/)) {
        const upath = join(mpath, u.name);
        const ufile = join(upath, "unit.yaml");
        const umeta = readYaml(ufile, unitSchema, issues);
        if (!umeta) continue;
        const expectedUnit = `${expectedModule}-u${two(u.order)}`;
        if (umeta.id !== expectedUnit || umeta.order !== u.order) {
          issues.push({ file: ufile, message: `id/order must be “${expectedUnit}” / ${u.order} to match the folder`, severity: "error" });
        }
        const unit: UnitNode = { meta: umeta, lessons: [] };
        for (const l of subdirs(upath, /^l(\d{2})-/)) {
          const lfile = join(upath, l.name, "lesson.yaml");
          const lmeta = readYaml(lfile, lessonSchema, issues);
          if (!lmeta) continue;
          const expectedLesson = `${expectedUnit}-l${two(l.order)}`;
          if (lmeta.id !== expectedLesson) {
            issues.push({ file: lfile, message: `id must be “${expectedLesson}” to match the folder`, severity: "error" });
          }
          unit.lessons.push({ meta: lmeta, order: l.order, file: lfile });
        }
        mod.units.push(unit);
      }
      course.modules.push(mod);
    }
    courses.push(course);
  }
  const seen = new Map<string, string>();
  for (const c of courses)
    for (const m of c.modules)
      for (const u of m.units)
        for (const l of u.lessons) {
          const prev = seen.get(l.meta.id);
          if (prev) issues.push({ file: l.file, message: `Duplicate lesson id also used in ${prev}`, severity: "error" });
          seen.set(l.meta.id, l.file);
        }
  return { courses, issues };
}

export function loadContentOrThrow(contentDir: string): ContentTree {
  const tree = loadContent(contentDir);
  const errors = tree.issues.filter((i) => i.severity === "error");
  if (errors.length > 0) {
    throw new Error(`Content is invalid:\n${errors.map((e) => `  ${e.file}: ${e.message}`).join("\n")}`);
  }
  return tree;
}

export function findLesson(tree: ContentTree, lessonId: string): { course: CourseNode; module: ModuleNode; unit: UnitNode; lesson: LessonNode } | null {
  for (const course of tree.courses)
    for (const module of course.modules)
      for (const unit of module.units)
        for (const lesson of unit.lessons) if (lesson.meta.id === lessonId) return { course, module, unit, lesson };
  return null;
}

export function allLessons(tree: ContentTree): LessonNode[] {
  return tree.courses.flatMap((c) => c.modules.flatMap((m) => m.units.flatMap((u) => u.lessons)));
}
