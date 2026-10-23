import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { resolve } from "node:path";
import { schema, type DbHandle } from "@allmaths/db";
import { openTestDb } from "@allmaths/db/testing";
import { canOpenCourse, dbSectionId, enrollInCourse, getDashboard, getEnrolledCourseId, listCourseCards, loadStore, registerStudent, syncContent, type ContentStore } from "../src";

let h: DbHandle;
let store: ContentStore;
let userId: string;
beforeAll(async () => {
  h = await openTestDb();
  store = loadStore(resolve(import.meta.dirname, "..", "..", "..", "content"));
  await syncContent(h.db, store);
  userId = (await registerStudent(h.db, { email: "enrol@example.com", name: "Enrol", password: "enrol password 12" })).id;
});
afterAll(async () => {
  await h.close();
});

describe("one course at a time", () => {
  it("a new learner follows no course until they enroll", async () => {
    expect(await getEnrolledCourseId(h.db, userId)).toBeNull();
    expect(canOpenCourse("student", null, "geo")).toBe(false);
  });

  it("lists every course with its size", () => {
    const cards = listCourseCards(store);
    expect(cards.map((c) => c.id).sort()).toEqual(["geo", "mvc", "stat"]);
    for (const c of cards) expect(c.lessons).toBeGreaterThan(0);
  });

  it("enrolling opens that course only; switching closes the first and keeps the progress", async () => {
    await enrollInCourse(h.db, store, userId, "geo");
    expect(await getEnrolledCourseId(h.db, userId)).toBe("geo");
    expect(canOpenCourse("student", "geo", "geo")).toBe(true);
    expect(canOpenCourse("student", "geo", "mvc")).toBe(false);
    const dash = await getDashboard(h.db, store, userId, "geo");
    expect(dash.courses.map((c) => c.id)).toEqual(["geo"]);

    const lesson = store.courses.find((c) => c.meta.id === "geo")!.modules[0]!.units[0]!.lessons[0]!.meta.id;
    const sections = store.lesson(lesson)!.lesson.sections;
    for (const sec of sections.slice(0, Math.ceil(sections.length / 2)))
      await h.db.insert(schema.sectionProgress).values({ userId, lessonId: lesson, sectionId: dbSectionId(lesson, sec.id), completedAt: new Date() });
    await enrollInCourse(h.db, store, userId, "mvc");
    expect(await getEnrolledCourseId(h.db, userId)).toBe("mvc");
    expect((await h.db.select().from(schema.enrollments)).length).toBe(1);
    await enrollInCourse(h.db, store, userId, "geo");
    const back = await getDashboard(h.db, store, userId, "geo");
    expect(back.courses[0]!.modules[0]!.units[0]!.lessons[0]!.percent).toBeGreaterThan(0);
  });

  it("enrolling again in the same course changes nothing; an unknown course is refused", async () => {
    await enrollInCourse(h.db, store, userId, "geo");
    expect((await h.db.select().from(schema.enrollments)).length).toBe(1);
    await expect(enrollInCourse(h.db, store, userId, "nope")).rejects.toMatchObject({ code: "not_found" });
  });

  it("staff can open every course", () => {
    for (const role of ["instructor", "content_author", "reviewer", "admin"] as const) expect(canOpenCourse(role, null, "mvc")).toBe(true);
  });
});
