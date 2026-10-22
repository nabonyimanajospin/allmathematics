import { createHash } from "node:crypto";
import { and, eq, notInArray } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import type { ContentStore } from "./store";
import { dbSectionId } from "./store";

function hash(value: unknown): string {
  return createHash("sha256").update(JSON.stringify(value)).digest("hex");
}

/**
 * Makes the database rows for courses, modules, units, lessons and sections match the content files.
 * Idempotent. Progress rows reference sections, so a section that still exists keeps its progress;
 * a removed section is deleted (and its progress with it).
 */
export async function syncContent(db: AppDb, store: ContentStore): Promise<{ lessons: number; sections: number }> {
  let lessonCount = 0;
  let sectionCount = 0;
  await db.transaction(async (tx) => {
    for (const course of store.courses) {
      const c = course.meta;
      await tx
        .insert(schema.courses)
        .values({ id: c.id, slug: c.id, title: c.title, description: c.description, order: c.order, status: c.status })
        .onConflictDoUpdate({
          target: schema.courses.id,
          set: { title: c.title, description: c.description, order: c.order, status: c.status },
        });
      for (const module of course.modules) {
        const m = module.meta;
        await tx
          .insert(schema.modules)
          .values({ id: m.id, courseId: c.id, order: m.order, title: m.title, description: m.description, free: m.free })
          .onConflictDoUpdate({
            target: schema.modules.id,
            set: { order: m.order, title: m.title, description: m.description, free: m.free },
          });
        for (const unit of module.units) {
          const u = unit.meta;
          await tx
            .insert(schema.units)
            .values({ id: u.id, moduleId: m.id, order: u.order, title: u.title })
            .onConflictDoUpdate({ target: schema.units.id, set: { order: u.order, title: u.title } });
          for (const ln of unit.lessons) {
            const l = ln.meta;
            lessonCount++;
            const hasPractice = l.sections.some((s) => s.type === "practice");
            await tx
              .insert(schema.lessons)
              .values({
                id: l.id, unitId: u.id, order: ln.order, title: l.title, estMinutes: l.estMinutes,
                version: l.version, status: l.status, contentHash: hash(l), hasPractice, hasQuiz: false,
              })
              .onConflictDoUpdate({
                target: schema.lessons.id,
                set: {
                  order: ln.order, title: l.title, estMinutes: l.estMinutes, version: l.version,
                  status: l.status, contentHash: hash(l), hasPractice, hasQuiz: false,
                },
              });
            const ids: string[] = [];
            for (const [i, s] of l.sections.entries()) {
              sectionCount++;
              const id = dbSectionId(l.id, s.id);
              ids.push(id);
              await tx
                .insert(schema.sections)
                .values({ id, lessonId: l.id, order: i + 1, type: s.type, minSeconds: s.minSeconds ?? null, contentJson: s })
                .onConflictDoUpdate({
                  target: schema.sections.id,
                  set: { lessonId: l.id, order: i + 1, type: s.type, minSeconds: s.minSeconds ?? null, contentJson: s },
                });
            }
            await tx
              .delete(schema.sections)
              .where(and(eq(schema.sections.lessonId, l.id), notInArray(schema.sections.id, ids)));
          }
        }
      }
    }
  });
  return { lessons: lessonCount, sections: sectionCount };
}
