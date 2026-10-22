import { randomUUID } from "node:crypto";
import { eq } from "drizzle-orm";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { schema } from "@allmaths/db";
import { checkAnswer, getDashboard, getHint, getLessonState, ingestEvents, revealSolution, syncContent } from "../src";
import { completeLesson, engine, ev, makeFixture, readSection, type Fixture } from "./helpers";

const L1 = "geo-m01-u01-l01";
const L2 = "geo-m01-u01-l02";
const L3 = "geo-m01-u01-l03";
const T0 = new Date("2026-10-21T10:00:00Z");
const at = (secs: number) => new Date(T0.getTime() + secs * 1000);

let f: Fixture;
beforeAll(async () => {
  f = await makeFixture({ geometryModule1Only: true });
  if (!(await engine.health())) {
    if (process.env.REQUIRE_ENGINE === "1") throw new Error("Math engine is required but not running");
    throw new Error("Start the math engine on :8001 (see docs/running.md) to run these tests");
  }
});
afterAll(async () => {
  await f.h.close();
});

const deps = () => ({ db: f.h.db, store: f.store, engine });

describe("content sync", () => {
  it("writes the hierarchy and is idempotent", async () => {
    const first = await syncContent(f.h.db, f.store);
    const again = await syncContent(f.h.db, f.store);
    expect(first).toEqual(again);
    const inStore = f.store.courses.flatMap((c) => c.modules.flatMap((m) => m.units.flatMap((u) => u.lessons))).length;
    expect(first.lessons).toBe(inStore);
    const lessons = await f.h.db.select().from(schema.lessons);
    expect(lessons).toHaveLength(inStore);
    expect(lessons.filter((l) => l.unitId === "geo-m01-u01").map((l) => l.id).sort()).toEqual([L1, L2, L3]);
    const [mod] = await f.h.db.select().from(schema.modules).where(eq(schema.modules.id, "geo-m01"));
    expect(mod?.free).toBe(true);
  });
});

describe("Phase 1 acceptance: progress moves after each section and survives a refresh", () => {
  it("starts at 0 and resumes at the first section", async () => {
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.progress.lesson.percent).toBe(0);
    expect(s.completedSectionIds).toEqual([]);
    expect(s.resumeSectionId).toBe("why-vectors");
  });

  it("does not complete a section before the minimum time", async () => {
    await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId: L1, sectionId: "why-vectors" })], at(0));
    const r = await ingestEvents(
      f.h.db, f.store, f.userId,
      [ev({ verb: "viewed", lessonId: L1, sectionId: "why-vectors", result: { durationMs: 19_000 } })], at(19),
    );
    expect(r.progress[L1]?.lesson.percent).toBe(0);
  });

  it("completes it at 20 seconds of concept reading and the bar rises", async () => {
    const r = await ingestEvents(
      f.h.db, f.store, f.userId,
      [ev({ verb: "viewed", lessonId: L1, sectionId: "why-vectors", result: { durationMs: 1_000 } })], at(20),
    );
    // Lesson 1 has 14 sections: 1/14 of the lesson = 7.14...% -> 7
    expect(f.store.lesson(L1)!.lesson.sections).toHaveLength(14);
    expect(r.progress[L1]?.lesson.percent).toBe(7);
    expect(r.progress[L1]?.lesson.exact).toBe("1/14");
  });

  it("a page refresh gives exactly the same state", async () => {
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.completedSectionIds).toEqual(["why-vectors"]);
    expect(s.progress.lesson.percent).toBe(7);
    expect(s.nextIncompleteSectionId).toBe("vector-ab");
    expect(s.resumeSectionId).toBe("vector-ab");
  });

  it("each following section raises the bar", async () => {
    let last = 7;
    let t = at(30);
    for (const id of ["vector-ab", "components-formula", "ex-components-plane"]) {
      await readSection(f, L1, id, t);
      const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
      expect(s.progress.lesson.percent).toBeGreaterThan(last);
      last = s.progress.lesson.percent;
      t = new Date(t.getTime() + 60_000);
    }
  });

  it("resumes at the section last touched, not the first one", async () => {
    await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId: L1, sectionId: "equality-free" })], at(500));
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.resumeSectionId).toBe("equality-free");
  });
});

describe("idempotent and tamper-resistant event ingestion", () => {
  it("a re-delivered event never double-counts", async () => {
    const e = ev({ verb: "viewed", lessonId: L2, sectionId: "adding-vectors", result: { durationMs: 30_000 } });
    await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId: L2, sectionId: "adding-vectors" })], at(1000));
    const first = await ingestEvents(f.h.db, f.store, f.userId, [e], at(1030));
    const second = await ingestEvents(f.h.db, f.store, f.userId, [e, e], at(1031));
    expect(first.accepted).toBe(1);
    expect(second.accepted).toBe(0);
    expect(second.duplicates).toBe(2);
    const rows = await f.h.db.select().from(schema.events).where(eq(schema.events.id, e.eventId));
    expect(rows).toHaveLength(1);
    const [sp] = await f.h.db.select().from(schema.sectionProgress).where(eq(schema.sectionProgress.sectionId, `${L2}-adding-vectors`));
    expect(sp?.activeMs).toBe(30_000);
  });

  it("credits no more time than the server clock allows (claiming 10 minutes after 2 seconds)", async () => {
    await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId: L2, sectionId: "chasles" })], at(2000));
    const r = await ingestEvents(
      f.h.db, f.store, f.userId,
      [ev({ verb: "viewed", lessonId: L2, sectionId: "chasles", result: { durationMs: 600_000 } })], at(2002),
    );
    const s = (await getLessonState(f.h.db, f.store, f.userId, L2))!;
    expect(s.completedSectionIds).not.toContain("chasles");
    const [sp] = await f.h.db.select().from(schema.sectionProgress).where(eq(schema.sectionProgress.sectionId, `${L2}-chasles`));
    expect(sp!.activeMs).toBeLessThanOrEqual(2_000);
    expect(r.progress[L2]?.lesson.percent).toBeLessThan(10);
  });

  it("the same elapsed time cannot be claimed twice", async () => {
    const sec = "sum-components";
    await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId: L2, sectionId: sec })], at(3000));
    for (let i = 0; i < 5; i++) {
      await ingestEvents(
        f.h.db, f.store, f.userId,
        [ev({ verb: "viewed", lessonId: L2, sectionId: sec, result: { durationMs: 8_000 } })], at(3001 + i),
      );
    }
    const [sp] = await f.h.db.select().from(schema.sectionProgress).where(eq(schema.sectionProgress.sectionId, `${L2}-${sec}`));
    // Five claims of 8 s each, but only 4 s of real time passed since the first event: at most 4 s credited.
    expect(sp!.activeMs).toBeLessThanOrEqual(5_000);
    expect(sp!.completedAt).toBeNull();
  });

  it("a check can never be completed by viewing", async () => {
    await ingestEvents(f.h.db, f.store, f.userId, [ev({ verb: "started", lessonId: L1, sectionId: "chk-components" })], at(4000));
    await ingestEvents(
      f.h.db, f.store, f.userId,
      [ev({ verb: "viewed", lessonId: L1, sectionId: "chk-components", result: { durationMs: 600_000 } })], at(4600),
    );
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.completedSectionIds).not.toContain("chk-components");
  });

  it("rejects forged verbs, unknown lessons and unknown sections without failing the batch", async () => {
    const good = ev({ verb: "started", lessonId: L3, sectionId: "collinear" });
    const r = await ingestEvents(
      f.h.db, f.store, f.userId,
      [
        ev({ verb: "passed", lessonId: L1 }),
        ev({ verb: "answered", lessonId: L1, sectionId: "chk-components", result: { correct: true } }),
        ev({ verb: "viewed", lessonId: "geo-m09-u09-l09" }),
        ev({ verb: "viewed", lessonId: L1, sectionId: "no-such-section" }),
        good,
      ],
      at(5000),
    );
    expect(r.accepted).toBe(1);
    expect(r.rejected.map((x) => x.reason)).toEqual(["verb_not_allowed", "verb_not_allowed", "unknown_lesson", "unknown_section"]);
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.completedSectionIds).not.toContain("chk-components");
  });

  it("one user's events never change another user's progress", async () => {
    const [other] = await f.h.db.insert(schema.users).values({ email: `${randomUUID()}@example.com`, name: "O" }).returning();
    const s = (await getLessonState(f.h.db, f.store, other!.id, L1))!;
    expect(s.progress.lesson.percent).toBe(0);
    expect(s.completedSectionIds).toEqual([]);
  });
});

describe("check questions", () => {
  it("accepts an equivalent exact form and completes the section", async () => {
    const r = await checkAnswer(deps(), f.userId, L1, "chk-components", "(3,-4)", at(6000));
    expect(r.status).toBe("correct");
    expect(r.explanation).toContain("(3,-4)");
    expect(r.progress?.lesson.percent).toBeGreaterThan(0);
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.completedSectionIds).toContain("chk-components");
  });

  it("a wrong answer is recorded, completes nothing and returns the targeted hint", async () => {
    const r = await checkAnswer(deps(), f.userId, L1, "chk-space", "(3,-5,-4)", at(6100));
    expect(r.status).toBe("incorrect");
    expect(r.hint).toContain("end");
    expect(r.explanation).toBeUndefined();
    const s = (await getLessonState(f.h.db, f.store, f.userId, L1))!;
    expect(s.completedSectionIds).not.toContain("chk-space");
    const answered = await f.h.db.select().from(schema.events).where(eq(schema.events.verb, "answered"));
    expect(answered.length).toBeGreaterThanOrEqual(2);
  });

  it("refuses decimals without counting an attempt", async () => {
    const before = (await f.h.db.select().from(schema.events).where(eq(schema.events.verb, "answered"))).length;
    const r = await checkAnswer(deps(), f.userId, L3, "chk-collinear-k", "4.0", at(6200));
    expect(r.status).toBe("invalid");
    expect(r.code).toBe("decimal_not_allowed");
    const after = (await f.h.db.select().from(schema.events).where(eq(schema.events.verb, "answered"))).length;
    expect(after).toBe(before);
  });

  it("accepts LaTeX from the math keyboard", async () => {
    const r = await checkAnswer(deps(), f.userId, L3, "chk-coordinates", "\\left(\\frac{18}{5},\\frac{11}{5}\\right)", at(6300));
    expect(r.status).toBe("correct");
    expect(r.studentLatex).toContain("18");
  });

  it("multiple choice compares the chosen index", async () => {
    expect((await checkAnswer(deps(), f.userId, L1, "chk-opposite", "1", at(6400))).status).toBe("incorrect");
    expect((await checkAnswer(deps(), f.userId, L1, "chk-opposite", "0", at(6401))).status).toBe("correct");
  });

  it("unknown questions and non-check sections are not found", async () => {
    await expect(checkAnswer(deps(), f.userId, L1, "why-vectors", "1", at(6500))).rejects.toMatchObject({ status: 404 });
    await expect(checkAnswer(deps(), f.userId, "nope-m01-u01-l01", "x", "1", at(6500))).rejects.toMatchObject({ status: 404 });
  });

  it("hints come one at a time, in order, and are counted", async () => {
    await expect(getHint(deps(), f.userId, L3, "chk-basis-3d", 1, at(7000))).rejects.toMatchObject({ code: "hint_locked" });
    const h1 = await getHint(deps(), f.userId, L3, "chk-basis-3d", 0, at(7001));
    expect(h1.hintsUsed).toBe(1);
    expect(h1.hintCount).toBe(2);
    const again = await getHint(deps(), f.userId, L3, "chk-basis-3d", 0, at(7002));
    expect(again.hintsUsed).toBe(1);
    const h2 = await getHint(deps(), f.userId, L3, "chk-basis-3d", 1, at(7003));
    expect(h2.hintsUsed).toBe(2);
    await expect(getHint(deps(), f.userId, L3, "chk-basis-3d", 2, at(7004))).rejects.toMatchObject({ code: "no_such_hint" });
    const hinted = await f.h.db.select().from(schema.events).where(eq(schema.events.verb, "hinted"));
    expect(hinted.length).toBeGreaterThanOrEqual(2);
    const s = (await getLessonState(f.h.db, f.store, f.userId, L3))!;
    expect(s.hintsUsed["chk-basis-3d"]).toBe(2);
  });

  it("revealing the explanation does not complete the question", async () => {
    const r = await revealSolution(deps(), f.userId, L3, "chk-basis-3d", at(7100));
    expect(r.explanation).toContain("13");
    const s = (await getLessonState(f.h.db, f.store, f.userId, L3))!;
    expect(s.completedSectionIds).not.toContain("chk-basis-3d");
  });
});

describe("progress formulas applied end to end", () => {
  let g: Fixture;
  beforeAll(async () => {
    g = await makeFixture({ geometryModule1Only: true });
  });
  afterAll(async () => {
    await g.h.close();
  });

  it("completing lesson 1 gives 100% for the lesson and the exact weighted share above it", async () => {
    await completeLesson(g, L1);
    const s = (await getLessonState(g.h.db, g.store, g.userId, L1))!;
    expect(s.progress.lesson).toEqual({ exact: "1", percent: 100 });
    // lessons weigh 25, 30 and 35 minutes: unit = 25/90 = 27.7...% -> 27 (rounded down)
    expect(s.progress.unit).toEqual({ exact: "5/18", percent: 27 });
    expect(s.progress.module.exact).toBe("5/18");
    expect(s.progress.course.exact).toBe("5/18");
  });

  it("completing all three lessons gives exactly 100% everywhere", async () => {
    await completeLesson(g, L2, new Date("2026-10-22T10:00:00Z"));
    await completeLesson(g, L3, new Date("2026-10-23T10:00:00Z"));
    const s = (await getLessonState(g.h.db, g.store, g.userId, L3))!;
    expect(s.progress.unit).toEqual({ exact: "1", percent: 100 });
    expect(s.progress.course).toEqual({ exact: "1", percent: 100 });
    expect(s.nextIncompleteSectionId).toBeNull();
  });

  it("the dashboard matches the stored progress and points to the next lesson", async () => {
    const h = await makeFixture({ geometryModule1Only: true });
    try {
      await completeLesson(h, L1);
      const d = await getDashboard(h.h.db, h.store, h.userId);
      const unit = d.courses[0]!.modules[0]!.units[0]!;
      expect(unit.percent).toBe(27);
      expect(unit.lessons.map((l) => l.percent)).toEqual([100, 0, 0]);
      expect(d.continueLessonId).toBe(L2);
      await readSection(h, L2, "adding-vectors", new Date("2026-10-22T10:00:00Z"));
      const d2 = await getDashboard(h.h.db, h.store, h.userId);
      expect(d2.continueLessonId).toBe(L2);
    } finally {
      await h.h.close();
    }
  });
});
