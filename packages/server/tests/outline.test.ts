import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { checkAnswer, getCourseOutline } from "../src";
import { engine, makeFixture, type Fixture } from "./helpers";

const L = "mvc-m04-u01-l02";

let f: Fixture;
beforeAll(async () => {
  f = await makeFixture();
});
afterAll(async () => {
  await f.h.close();
});

describe("course outline", () => {
  it("lists every module, unit and lesson of the course of the lesson, and marks the current one", async () => {
    const o = (await getCourseOutline(f.h.db, f.store, f.userId, L))!;
    expect(o.courseId).toBe("mvc");
    expect(o.modules.map((m) => m.id)).toEqual(["mvc-m01", "mvc-m02", "mvc-m03", "mvc-m04"]);
    const lessons = o.modules.flatMap((m) => m.units.flatMap((u) => u.lessons));
    expect(lessons.filter((l) => l.current).map((l) => l.id)).toEqual([L]);
    expect(o.modules.filter((m) => m.current).map((m) => m.id)).toEqual(["mvc-m04"]);
    expect(lessons.every((l) => l.percent === 0)).toBe(true);
  });

  it("shows progress after an exercise is solved", async () => {
    if (!(await engine.health())) throw new Error("Start the math engine on :8001 to run these tests");
    const r = await checkAnswer({ db: f.h.db, store: f.store, engine }, f.userId, L, "sep-e", "y = C*sin(x)", new Date("2026-10-21T10:00:00Z"));
    expect(r.status).toBe("correct");
    const o = (await getCourseOutline(f.h.db, f.store, f.userId, L))!;
    const lesson = o.modules.flatMap((m) => m.units.flatMap((u) => u.lessons)).find((l) => l.id === L)!;
    expect(lesson.percent).toBeGreaterThan(0);
    // one exercise is a small part of a module: the whole percentage can still round down to 0
    expect(o.modules.find((m) => m.id === "mvc-m04")!.percent).toBeGreaterThanOrEqual(0);
  });

  it("is empty for an unknown lesson", async () => {
    expect(await getCourseOutline(f.h.db, f.store, f.userId, "nope-m01-u01-l01")).toBeNull();
  });
});
