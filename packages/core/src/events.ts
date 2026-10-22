/**
 * Learning events (spec section 9.1), inspired by xAPI.
 * Events are generated on the client with a UUID so that retries and duplicate deliveries are harmless
 * (the server stores each eventId once). The server never trusts a client for progress: it recomputes.
 */

import { z } from "zod";
import { DEFAULT_MIN_SECONDS } from "./progress";

export const VERBS = [
  "started",
  "viewed",
  "completed",
  "attempted",
  "answered",
  "hinted",
  "revealed_solution",
  "passed",
  "failed",
  "bookmarked",
  "resumed",
] as const;
export type Verb = (typeof VERBS)[number];

/** Verbs a browser may report. Everything else (answers, hints, passes) is recorded by the server itself. */
export const CLIENT_VERBS = ["started", "viewed", "resumed", "bookmarked"] as const;

export const MAX_BATCH = 50;
export const MAX_DURATION_MS = 10 * 60 * 1000;

const contentId = z
  .string()
  .min(3)
  .max(80)
  .regex(/^[a-z0-9][a-z0-9-]*$/, "Invalid id");

export const eventInputSchema = z.object({
  eventId: z.uuid(),
  verb: z.enum(VERBS),
  lessonId: contentId,
  sectionId: contentId.optional(),
  problemInstanceId: z.string().max(80).optional(),
  result: z
    .object({
      correct: z.boolean().optional(),
      score: z.number().int().min(0).max(1000).optional(),
      maxScore: z.number().int().min(0).max(1000).optional(),
      /** Active time on the object, claimed by the client; the server caps it by its own clock. */
      durationMs: z.number().int().min(0).max(MAX_DURATION_MS).optional(),
    })
    .optional(),
  clientTimestamp: z.number().int().min(0),
  device: z.enum(["mobile", "tablet", "desktop"]).optional(),
});
export type EventInput = z.infer<typeof eventInputSchema>;

export const eventBatchSchema = z.object({
  events: z.array(eventInputSchema).min(1).max(MAX_BATCH),
});
export type EventBatch = z.infer<typeof eventBatchSchema>;

/**
 * Active time the server is willing to credit: never more than what its own clock allows.
 * The caller advances its reference time by the credited amount, so the same elapsed time can never be
 * credited twice and the total credited can never exceed the real time since the section was opened.
 */
export function creditedDurationMs(claimedMs: number, serverElapsedMs: number, slackMs = 0): number {
  const claimed = Math.max(0, Math.min(claimedMs, MAX_DURATION_MS));
  const allowed = Math.max(0, serverElapsedMs) + slackMs;
  return Math.min(claimed, allowed);
}

export interface SectionRule {
  type: string;
  /** Overrides the default minimum for the block type. */
  minSeconds?: number | undefined;
}

export function requiredSeconds(rule: SectionRule): number {
  if (rule.type === "check") return Infinity;
  return rule.minSeconds ?? DEFAULT_MIN_SECONDS[rule.type] ?? 15;
}

/**
 * A section is complete when
 *   - it is a `check` and the student has answered it correctly, or
 *   - it is any other block and the credited active time reached the minimum.
 */
export function isSectionComplete(rule: SectionRule, activeMs: number, checkAnsweredCorrectly: boolean): boolean {
  if (rule.type === "check") return checkAnsweredCorrectly;
  return activeMs >= requiredSeconds(rule) * 1000;
}
