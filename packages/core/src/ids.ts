/** Stable content ids: geo-m01-u01-l01 (course, module, unit, lesson) and geo-m01-u01-l01-<section>. */

export const COURSE_CODES = ["geo", "mvc", "stat"] as const;
export type CourseCode = (typeof COURSE_CODES)[number];

const LESSON_ID = /^([a-z]{3,5})-m(\d{2})-u(\d{2})-l(\d{2})$/;

export interface LessonIdParts {
  course: string;
  module: number;
  unit: number;
  lesson: number;
  moduleId: string;
  unitId: string;
  lessonId: string;
}

export function parseLessonId(id: string): LessonIdParts | null {
  const m = LESSON_ID.exec(id);
  if (!m) return null;
  const [, course, mm, uu, ll] = m as unknown as [string, string, string, string, string];
  return {
    course,
    module: Number(mm),
    unit: Number(uu),
    lesson: Number(ll),
    moduleId: `${course}-m${mm}`,
    unitId: `${course}-m${mm}-u${uu}`,
    lessonId: id,
  };
}

export function sectionDbId(lessonId: string, sectionSlug: string): string {
  return `${lessonId}-${sectionSlug}`;
}
