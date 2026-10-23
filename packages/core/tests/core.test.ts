import { describe, expect, it } from "vitest";
import {
  courseProgress,
  createEngineClient,
  EngineUnavailableError,
  creditedDurationMs,
  eventBatchSchema,
  isSectionComplete,
  lessonProgress,
  moduleProgress,
  parseLessonId,
  rational,
  unitProgress,
  unitProgressWithTest,
  type LessonInputs,
} from "../src";

const { frac, percentFloor, toString: show } = rational;

const full = (o: Partial<LessonInputs>): LessonInputs => ({
  sectionsCompleted: 0,
  sectionsTotal: 10,
  practiceSolved: 0,
  practiceTotal: 10,
  quizPassed: false,
  hasPractice: true,
  hasQuiz: true,
  ...o,
});

describe("lessonProgress (spec 9.2: 0.40 sections + 0.20 practice + 0.40 quiz)", () => {
  it("is 0 at the start and 1 when everything is done", () => {
    expect(show(lessonProgress(full({})))).toBe("0");
    expect(show(lessonProgress(full({ sectionsCompleted: 10, practiceSolved: 10, quizPassed: true })))).toBe("1");
  });

  it("weights each component exactly", () => {
    expect(show(lessonProgress(full({ sectionsCompleted: 10 })))).toBe("2/5"); // 0.40
    expect(show(lessonProgress(full({ practiceSolved: 10 })))).toBe("1/5"); // 0.20
    expect(show(lessonProgress(full({ quizPassed: true })))).toBe("2/5"); // 0.40
    expect(show(lessonProgress(full({ sectionsCompleted: 5 })))).toBe("1/5"); // 0.40 * 1/2
    expect(show(lessonProgress(full({ practiceSolved: 3 })))).toBe("3/50"); // 0.20 * 3/10
  });

  it("needs every exercise of the lesson, whether it has 3 or 25", () => {
    for (const n of [1, 3, 7, 15, 25]) {
      const base = { sectionsCompleted: 10, practiceTotal: n, hasQuiz: false };
      expect(show(lessonProgress(full({ ...base, practiceSolved: n })))).toBe("1");
      expect(percentFloor(lessonProgress(full({ ...base, practiceSolved: n - 1 })))).toBeLessThan(100);
    }
    // 12 of 25 exercises and all sections: 2/3 + 1/3 * 12/25 = 0.826..., shown as 82
    expect(percentFloor(lessonProgress(full({ sectionsCompleted: 10, practiceSolved: 12, practiceTotal: 25, hasQuiz: false })))).toBe(82);
  });

  it("never shows 100% before everything is complete", () => {
    const almost = lessonProgress(full({ sectionsCompleted: 10, practiceSolved: 10, quizPassed: false }));
    expect(percentFloor(almost)).toBe(60);
    const nearly = lessonProgress(full({ sectionsCompleted: 9, practiceSolved: 10, quizPassed: true }));
    expect(percentFloor(nearly)).toBe(96); // 100 - 4, not rounded up to 100
  });

  it("is monotone in sections completed", () => {
    let prev = frac(-1);
    for (let s = 0; s <= 10; s++) {
      const p = lessonProgress(full({ sectionsCompleted: s }));
      expect(rational.lte(prev, p)).toBe(true);
      prev = p;
    }
  });

  it("renormalises when the lesson has no practice or quiz yet (Phase 1 lessons)", () => {
    const only = (s: number) => lessonProgress(full({ sectionsCompleted: s, hasPractice: false, hasQuiz: false }));
    expect(show(only(0))).toBe("0");
    expect(show(only(5))).toBe("1/2");
    expect(show(only(10))).toBe("1");
    const noQuiz = lessonProgress(full({ sectionsCompleted: 10, practiceSolved: 10, hasQuiz: false }));
    expect(show(noQuiz)).toBe("1");
  });

  it("validates inputs", () => {
    expect(() => lessonProgress(full({ sectionsCompleted: 11 }))).toThrow();
    expect(() => lessonProgress(full({ sectionsCompleted: -1 }))).toThrow();
    expect(() => lessonProgress(full({ practiceSolved: 1.5 }))).toThrow();
    expect(() => lessonProgress(full({ practiceSolved: 11 }))).toThrow();
    expect(() => lessonProgress(full({ practiceTotal: 0 }))).toThrow();
  });
});

describe("unit progress with the unit test", () => {
  const lessons = [
    { weight: 30, progress: frac(1) },
    { weight: 30, progress: frac(1) },
  ];
  it("is the lessons alone when the unit has no test", () => {
    expect(show(unitProgressWithTest(lessons, { exists: false, passed: false }))).toBe("1");
  });
  it("is 80% when every lesson is done but the test is not passed, and 100% only when it is passed", () => {
    expect(show(unitProgressWithTest(lessons, { exists: true, passed: false }))).toBe("4/5");
    expect(percentFloor(unitProgressWithTest(lessons, { exists: true, passed: false }))).toBe(80);
    expect(show(unitProgressWithTest(lessons, { exists: true, passed: true }))).toBe("1");
  });
  it("passing the test alone, with no lessons done, gives 20%", () => {
    const none = [{ weight: 30, progress: frac(0) }];
    expect(percentFloor(unitProgressWithTest(none, { exists: true, passed: true }))).toBe(20);
  });
});

describe("unit / module / course progress", () => {
  it("weights lessons by estimated minutes", () => {
    const p = unitProgress([
      { weight: 30, progress: frac(1) },
      { weight: 10, progress: frac(0) },
    ]);
    expect(show(p)).toBe("3/4");
  });

  it("module: 80% units + 20% module test", () => {
    const units = [{ weight: 20, progress: frac(1) }];
    expect(show(moduleProgress(units, { exists: true, passed: false }))).toBe("4/5");
    expect(show(moduleProgress(units, { exists: true, passed: true }))).toBe("1");
    expect(show(moduleProgress(units, { exists: false, passed: false }))).toBe("1");
  });

  it("module test alone is worth exactly 20%", () => {
    const units = [{ weight: 20, progress: frac(0) }];
    expect(percentFloor(moduleProgress(units, { exists: true, passed: true }))).toBe(20);
  });

  it("course: weighted average of modules", () => {
    const p = courseProgress([
      { weight: 100, progress: frac(1, 2) },
      { weight: 300, progress: frac(1) },
    ]);
    expect(show(p)).toBe("7/8");
    expect(percentFloor(p)).toBe(87); // floor of 87.5
  });

  it("empty input is 0", () => {
    expect(show(unitProgress([]))).toBe("0");
  });
});

describe("percentFloor", () => {
  it("rounds down and clamps", () => {
    expect(percentFloor(frac(1, 3))).toBe(33);
    expect(percentFloor(frac(2, 3))).toBe(66);
    expect(percentFloor(frac(199, 200))).toBe(99);
    expect(percentFloor(frac(1))).toBe(100);
    expect(percentFloor(frac(5, 4))).toBe(100);
    expect(percentFloor(frac(-1, 4))).toBe(0);
  });
});

describe("section completion", () => {
  it("non-check blocks need the minimum active time (default 20 s for concept)", () => {
    expect(isSectionComplete({ type: "concept" }, 19_999, false)).toBe(false);
    expect(isSectionComplete({ type: "concept" }, 20_000, false)).toBe(true);
    expect(isSectionComplete({ type: "concept", minSeconds: 5 }, 5_000, false)).toBe(true);
  });

  it("check blocks need a correct answer, never time", () => {
    expect(isSectionComplete({ type: "check" }, 10 * 60_000, false)).toBe(false);
    expect(isSectionComplete({ type: "check" }, 0, true)).toBe(true);
  });

  it("credited duration is bounded by the server clock", () => {
    expect(creditedDurationMs(60_000, 3_000)).toBe(3_000);
    expect(creditedDurationMs(4_000, 30_000)).toBe(4_000);
    expect(creditedDurationMs(-5, 1_000)).toBe(0);
    expect(creditedDurationMs(99_999_999, 99_999_999)).toBe(600_000);
  });
});

describe("event schema", () => {
  const ok = {
    eventId: "6f1c3b0e-5c1b-4a43-9d58-0d3f0b0f7a11",
    verb: "viewed",
    lessonId: "geo-m01-u01-l01",
    sectionId: "geo-m01-u01-l01-intro",
    result: { durationMs: 21000 },
    clientTimestamp: 1_790_000_000_000,
  };

  it("accepts a valid batch", () => {
    expect(eventBatchSchema.safeParse({ events: [ok] }).success).toBe(true);
  });

  it("rejects bad ids, verbs, sizes", () => {
    expect(eventBatchSchema.safeParse({ events: [{ ...ok, eventId: "nope" }] }).success).toBe(false);
    expect(eventBatchSchema.safeParse({ events: [{ ...ok, verb: "hacked" }] }).success).toBe(false);
    expect(eventBatchSchema.safeParse({ events: [{ ...ok, lessonId: "../etc" }] }).success).toBe(false);
    expect(eventBatchSchema.safeParse({ events: [] }).success).toBe(false);
    expect(eventBatchSchema.safeParse({ events: Array(51).fill(ok) }).success).toBe(false);
    expect(eventBatchSchema.safeParse({ events: [{ ...ok, result: { durationMs: 9e9 } }] }).success).toBe(false);
  });
});

describe("ids", () => {
  it("parses lesson ids", () => {
    expect(parseLessonId("geo-m01-u01-l03")).toMatchObject({
      course: "geo",
      module: 1,
      unit: 1,
      lesson: 3,
      moduleId: "geo-m01",
      unitId: "geo-m01-u01",
    });
    expect(parseLessonId("geo-m1-u1-l1")).toBeNull();
    expect(parseLessonId("../x")).toBeNull();
  });
});

describe("engine client resilience", () => {
  const ok = (body: unknown) => new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
  const verified = { equal: true };

  it("retries a network failure and then succeeds", async () => {
    let calls = 0;
    const fetchImpl = (async () => {
      calls++;
      if (calls < 3) throw new TypeError("fetch failed");
      return ok(verified);
    }) as typeof fetch;
    const c = createEngineClient({ url: "http://engine", token: "t", fetchImpl, retryDelayMs: 1 });
    expect((await c.verify("1", "1")).equal).toBe(true);
    expect(calls).toBe(3);
  });

  it("retries HTTP 5xx", async () => {
    let calls = 0;
    const fetchImpl = (async () => (++calls < 2 ? new Response("boom", { status: 503 }) : ok(verified))) as typeof fetch;
    const c = createEngineClient({ url: "http://engine", token: "t", fetchImpl, retryDelayMs: 1 });
    await c.verify("1", "1");
    expect(calls).toBe(2);
  });

  it("gives up after the retries and reports the engine as unavailable", async () => {
    let calls = 0;
    const fetchImpl = (async () => {
      calls++;
      throw new TypeError("fetch failed");
    }) as typeof fetch;
    const c = createEngineClient({ url: "http://engine", token: "t", fetchImpl, retryDelayMs: 1 });
    await expect(c.verify("1", "1")).rejects.toBeInstanceOf(EngineUnavailableError);
    expect(calls).toBe(3);
  });

  it("does not retry client errors (4xx) or malformed responses", async () => {
    let calls = 0;
    const bad = (async () => (calls++, new Response("{}", { status: 401 }))) as typeof fetch;
    await expect(createEngineClient({ url: "http://e", token: "t", fetchImpl: bad, retryDelayMs: 1 }).verify("1", "1")).rejects.toBeInstanceOf(
      EngineUnavailableError,
    );
    expect(calls).toBe(1);
    calls = 0;
    const weird = (async () => (calls++, ok({ unexpected: true }))) as typeof fetch;
    await expect(createEngineClient({ url: "http://e", token: "t", fetchImpl: weird, retryDelayMs: 1 }).verify("1", "1")).rejects.toBeInstanceOf(
      EngineUnavailableError,
    );
    expect(calls).toBe(1);
  });

  it("sends the shared secret and JSON body", async () => {
    let seen: { headers: Headers; body: string } | undefined;
    const fetchImpl = (async (_u: unknown, init: RequestInit) => {
      seen = { headers: new Headers(init.headers), body: String(init.body) };
      return ok(verified);
    }) as typeof fetch;
    await createEngineClient({ url: "http://e/", token: "secret-token", fetchImpl }).verify("a", "b");
    expect(seen?.headers.get("x-engine-token")).toBe("secret-token");
    expect(JSON.parse(seen?.body ?? "{}")).toEqual({ a: "a", b: "b" });
  });
});
