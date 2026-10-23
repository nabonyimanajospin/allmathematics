/**
 * A learner follows one course at a time: they enroll in it, continue in it, and the other courses stay closed
 * until they switch. Switching keeps all progress, so coming back to a course resumes where they stopped.
 * Staff (any role except student) can open every course to review it.
 */

import { eq } from "drizzle-orm";
import { schema, type AppDb, type Role } from "@allmaths/db";
import type { ContentStore } from "../content/store";
import { Errors } from "../errors";

export interface CourseCard {
  id: string;
  title: string;
  description: string;
  modules: number;
  lessons: number;
  /** Estimated study time in whole hours (rounded up). */
  hours: number;
}

export function listCourseCards(store: ContentStore): CourseCard[] {
  return store.courses.map((c) => {
    const lessons = c.modules.flatMap((m) => m.units.flatMap((u) => u.lessons));
    const minutes = lessons.reduce((a, l) => a + l.meta.estMinutes, 0);
    return { id: c.meta.id, title: c.meta.title, description: c.meta.description, modules: c.modules.length, lessons: lessons.length, hours: Math.ceil(minutes / 60) };
  });
}

/** The course the learner is following now, or null. */
export async function getEnrolledCourseId(db: AppDb, userId: string): Promise<string | null> {
  const rows = await db.select({ courseId: schema.enrollments.courseId, startedAt: schema.enrollments.startedAt }).from(schema.enrollments).where(eq(schema.enrollments.userId, userId));
  rows.sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime());
  return rows[0]?.courseId ?? null;
}

/** Enrolls in a course; any other enrollment ends (progress is kept). Enrolling again in the same course changes nothing. */
export async function enrollInCourse(db: AppDb, store: ContentStore, userId: string, courseId: string, now = new Date()): Promise<void> {
  if (!store.courses.some((c) => c.meta.id === courseId)) throw Errors.notFound("Course not found");
  await db.transaction(async (tx) => {
    const current = await tx.select({ courseId: schema.enrollments.courseId }).from(schema.enrollments).where(eq(schema.enrollments.userId, userId));
    if (current.length === 1 && current[0]?.courseId === courseId) return;
    await tx.delete(schema.enrollments).where(eq(schema.enrollments.userId, userId));
    await tx.insert(schema.enrollments).values({ userId, courseId, source: "free", startedAt: now });
  });
}

/** True when this user may open lessons of the course. */
export function canOpenCourse(role: Role, enrolledCourseId: string | null, courseId: string): boolean {
  return role !== "student" || enrolledCourseId === courseId;
}
