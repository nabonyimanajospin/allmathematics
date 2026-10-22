/**
 * Event ingestion (spec section 9.1). Idempotent: an event id is stored once, so retries, duplicate
 * deliveries and `sendBeacon` re-sends never double-count. The browser may only report what it can
 * honestly observe (started, viewed with a duration, resumed, bookmarked); completion is decided here.
 */

import { and, eq, sql } from "drizzle-orm";
import { schema, type AppDb } from "@allmaths/db";
import { CLIENT_VERBS, creditedDurationMs, isSectionComplete, type EventInput } from "@allmaths/core";
import type { ContentStore } from "../content/store";
import { dbSectionId } from "../content/store";
import { recomputeProgress, type ProgressSnapshot } from "./progress";

export interface IngestResult {
  accepted: number;
  duplicates: number;
  rejected: { eventId: string; reason: string }[];
  progress: Record<string, ProgressSnapshot>;
}

/** Unused elapsed time that may still be claimed later (covers network delay between flushes). */
const BACKLOG_MS = 30_000;

const isClientVerb = (v: string): boolean => (CLIENT_VERBS as readonly string[]).includes(v);

export async function ingestEvents(
  db: AppDb,
  store: ContentStore,
  userId: string,
  events: readonly EventInput[],
  now = new Date(),
): Promise<IngestResult> {
  const result: IngestResult = { accepted: 0, duplicates: 0, rejected: [], progress: {} };
  const touchedLessons = new Set<string>();

  await db.transaction(async (tx) => {
    for (const ev of events) {
      if (!isClientVerb(ev.verb)) {
        result.rejected.push({ eventId: ev.eventId, reason: "verb_not_allowed" });
        continue;
      }
      const ref = store.lesson(ev.lessonId);
      if (!ref) {
        result.rejected.push({ eventId: ev.eventId, reason: "unknown_lesson" });
        continue;
      }
      const section = ev.sectionId ? ref.lesson.sections.find((s) => s.id === ev.sectionId) : undefined;
      if (ev.sectionId && !section) {
        result.rejected.push({ eventId: ev.eventId, reason: "unknown_section" });
        continue;
      }
      const sectionDb = section ? dbSectionId(ref.lesson.id, section.id) : undefined;

      const inserted = await tx
        .insert(schema.events)
        .values({
          id: ev.eventId,
          userId,
          verb: ev.verb,
          objectType: sectionDb ? "section" : "lesson",
          objectId: sectionDb ?? ref.lesson.id,
          lessonId: ref.lesson.id,
          sectionId: sectionDb ?? null,
          resultJson: ev.result ?? null,
          ts: now,
          clientTs: new Date(ev.clientTimestamp),
          device: ev.device ?? null,
        })
        .onConflictDoNothing()
        .returning({ id: schema.events.id });
      if (inserted.length === 0) {
        result.duplicates++;
        continue;
      }
      result.accepted++;

      if (!section || !sectionDb) continue;

      if (ev.verb === "started" || ev.verb === "resumed") {
        await tx
          .insert(schema.sectionProgress)
          .values({ userId, sectionId: sectionDb, lessonId: ref.lesson.id, openedAt: now, updatedAt: now })
          .onConflictDoUpdate({
            target: [schema.sectionProgress.userId, schema.sectionProgress.sectionId],
            set: { openedAt: now, updatedAt: now },
          });
      } else if (ev.verb === "viewed" && section.type !== "check") {
        await tx
          .insert(schema.sectionProgress)
          .values({ userId, sectionId: sectionDb, lessonId: ref.lesson.id, updatedAt: now })
          .onConflictDoNothing();
        const [row] = await tx
          .select()
          .from(schema.sectionProgress)
          .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.sectionId, sectionDb)))
          .for("update");
        if (row && !row.completedAt) {
          const elapsed = row.openedAt ? now.getTime() - row.openedAt.getTime() : 0;
          const credited = creditedDurationMs(ev.result?.durationMs ?? 0, elapsed);
          const activeMs = row.activeMs + credited;
          // Advance the reference point by what was credited (not to "now"): unused elapsed time stays
          // available for later claims, but never more than BACKLOG_MS, so idle time cannot pile up.
          const base = row.openedAt ? row.openedAt.getTime() + credited : now.getTime();
          const openedAt = new Date(Math.max(base, now.getTime() - BACKLOG_MS));
          const done = isSectionComplete({ type: section.type, minSeconds: section.minSeconds }, activeMs, false);
          await tx
            .update(schema.sectionProgress)
            .set({ activeMs, openedAt, updatedAt: now, completedAt: done ? now : null })
            .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.sectionId, sectionDb)));
        }
      } else if (ev.verb === "bookmarked") {
        await tx.insert(schema.bookmarks).values({ userId, sectionId: sectionDb }).onConflictDoNothing();
        continue;
      }
      touchedLessons.add(ref.lesson.id);
    }
    for (const lessonId of touchedLessons) {
      result.progress[lessonId] = await recomputeProgress(tx, store, userId, lessonId, now);
    }
  });
  return result;
}

/** Total credited active seconds for a user in a lesson (used by time-tracking reports). */
export async function activeSeconds(db: AppDb, userId: string, lessonId: string): Promise<number> {
  const [row] = await db
    .select({ ms: sql<string>`coalesce(sum(${schema.sectionProgress.activeMs}), 0)` })
    .from(schema.sectionProgress)
    .where(and(eq(schema.sectionProgress.userId, userId), eq(schema.sectionProgress.lessonId, lessonId)));
  return Math.floor(Number(row?.ms ?? 0) / 1000);
}
