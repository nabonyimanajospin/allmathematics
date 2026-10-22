import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  allLessons,
  lessonSchema,
  loadContent,
  toClientLesson,
  verifyLessonStatic,
  verifyLessonWithEngine,
  wordCount,
  type EngineClient,
  type Lesson,
} from "../src";

const contentDir = resolve(import.meta.dirname, "..", "..", "..", "content");
const tree = loadContent(contentDir);
const lessons = allLessons(tree);
const first = lessons[0]?.meta as Lesson;

function mutated(fn: (l: Lesson) => void): Lesson {
  const copy = structuredClone(first);
  fn(copy);
  return copy;
}
const errors = (l: Lesson) => verifyLessonStatic(l, "test.yaml").filter((i) => i.severity === "error");
const messages = (l: Lesson) => errors(l).map((e) => e.message);

describe("the real content", () => {
  it("loads without any issue", () => {
    expect(tree.issues).toEqual([]);
    expect(lessons.length).toBeGreaterThanOrEqual(3);
  });

  it("passes the static verification (KaTeX, notation lint, structure)", () => {
    for (const l of lessons) {
      expect(verifyLessonStatic(l.meta, l.file).filter((i) => i.severity === "error")).toEqual([]);
    }
  });

  it("has ids that follow the hierarchy", () => {
    expect(lessons.map((l) => l.meta.id)).toEqual(["geo-m01-u01-l01", "geo-m01-u01-l02", "geo-m01-u01-l03"]);
  });
});

describe("static verification catches mistakes", () => {
  it("notation: \\cdot between vectors", () => {
    const l = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body += "\n\nWrong: $\\vec u\\cdot\\vec v$.";
    });
    expect(messages(l).join("\n")).toContain("vector-dot-uses-cdot");
  });

  it("notation: \\times between vectors and plain-letter arguments", () => {
    const l = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body += "\n\n$\\vec u\\times\\vec v$ and $\\crossp{u}{v}$.";
    });
    const m = messages(l).join("\n");
    expect(m).toContain("vector-cross-uses-times");
    expect(m).toContain("vector-without-arrow");
  });

  it("decimals are errors, unless the block allows them", () => {
    const withDecimal = (allow: boolean) =>
      mutated((x) => {
        const s = x.sections.find((s) => s.type === "concept");
        if (s?.type === "concept") {
          s.body += "\n\nSo $x=3.5$.";
          if (allow) s.allowDecimal = true;
        }
      });
    expect(messages(withDecimal(false)).join("\n")).toContain("decimal-in-math");
    expect(messages(withDecimal(true)).join("\n")).not.toContain("decimal-in-math");
  });

  it("unrationalized denominators", () => {
    const l = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body += "\n\n$\\dfrac{1}{\\sqrt{2}}$";
    });
    expect(messages(l).join("\n")).toContain("unrationalized-denominator");
  });

  it("math that does not compile, and unbalanced dollars", () => {
    const bad = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body += "\n\n$\\unknowncommand{x}$";
    });
    expect(messages(bad).join("\n")).toContain("does not compile");
    const open = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body += "\n\nan $open formula";
    });
    expect(messages(open).join("\n")).toContain("unbalanced");
  });

  it("LaTeX outside dollar signs", () => {
    const l = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body += "\n\nthe vector \\vec u is long";
    });
    expect(messages(l).join("\n")).toContain("outside");
  });

  it("structure: summary last, example and check present", () => {
    const noSummary = mutated((x) => {
      x.sections = x.sections.filter((s) => s.type !== "summary");
    });
    expect(messages(noSummary).join("\n")).toContain("summary");
    const noCheck = mutated((x) => {
      x.sections = x.sections.filter((s) => s.type !== "check");
    });
    expect(messages(noCheck).join("\n")).toContain("check question");
  });

  it("answer keys must be exact", () => {
    const l = mutated((x) => {
      const s = x.sections.find((s) => s.type === "check");
      if (s?.type === "check") s.answer = "3.5";
    });
    expect(messages(l).join("\n")).toContain("decimal-in-math");
  });

  it("long concepts are rejected", () => {
    const l = mutated((x) => {
      const s = x.sections.find((s) => s.type === "concept");
      if (s?.type === "concept") s.body = Array(400).fill("word").join(" ");
    });
    expect(messages(l).join("\n")).toContain("words");
  });

  it("counts a formula as one word", () => {
    expect(wordCount("The vector $\\vec u=(1,2,3)$ has three components.")).toBe(6);
  });
});

describe("schema", () => {
  it("rejects unknown keys (typos) and duplicate section ids", () => {
    expect(lessonSchema.safeParse({ ...first, titel: "x" }).success).toBe(false);
    const dup = structuredClone(first);
    const s0 = dup.sections[0];
    if (s0) dup.sections[1] = { ...structuredClone(s0) };
    expect(lessonSchema.safeParse(dup).success).toBe(false);
  });

  it("multiple choice needs choices and a valid correctIndex", () => {
    const l = structuredClone(first);
    const idx = l.sections.findIndex((s) => s.type === "check");
    const c = l.sections[idx];
    if (c?.type === "check") {
      c.answerType = "multiple_choice";
      delete c.choices;
      delete c.correctIndex;
    }
    expect(lessonSchema.safeParse(l).success).toBe(false);
  });

  it("limits hints to three", () => {
    const l = structuredClone(first);
    const c = l.sections.find((s) => s.type === "check");
    if (c?.type === "check") c.hints = ["a", "b", "c", "d"];
    expect(lessonSchema.safeParse(l).success).toBe(false);
  });
});

describe("loader", () => {
  it("reports wrong ids and missing files without throwing", () => {
    const dir = mkdtempSync(join(tmpdir(), "allmaths-"));
    mkdirSync(join(dir, "geo", "m01-x", "u01-y", "l01-z"), { recursive: true });
    writeFileSync(join(dir, "geo", "course.yaml"), "id: geo\ntitle: G\ndescription: d\nstatus: draft\norder: 1\n");
    writeFileSync(join(dir, "geo", "m01-x", "module.yaml"), "id: geo-m02\ntitle: M\ndescription: d\norder: 1\n");
    writeFileSync(join(dir, "geo", "m01-x", "u01-y", "unit.yaml"), "id: geo-m01-u01\ntitle: U\norder: 1\n");
    const t = loadContent(dir);
    const msgs = t.issues.map((i) => i.message).join("\n");
    expect(msgs).toContain("geo-m01");
    expect(msgs).toContain("File is missing");
  });

  it("reports YAML syntax errors", () => {
    const dir = mkdtempSync(join(tmpdir(), "allmaths-"));
    mkdirSync(join(dir, "geo"), { recursive: true });
    writeFileSync(join(dir, "geo", "course.yaml"), "id: geo\n  bad: [unclosed\n");
    expect(loadContent(dir).issues[0]?.message).toContain("YAML");
  });
});

describe("client lesson never leaks secrets (spec section 13)", () => {
  it("removes keys, explanations, hints, mistakes and the correct choice", () => {
    for (const l of lessons) {
      const json = JSON.stringify(toClientLesson(l.meta));
      for (const s of l.meta.sections) {
        if (s.type !== "check") continue;
        expect(json).not.toContain(s.explanation.trim());
        for (const h of s.hints) expect(json).not.toContain(h.trim());
        for (const m of s.mistakes ?? []) expect(json).not.toContain(m.hint);
      }
      expect(json).not.toContain('"answer":"(');
      expect(json).not.toContain("correctIndex");
      expect(json).not.toContain('"value"');
      expect(json).not.toContain("explanation");
    }
  });

  it("keeps hint counts and choice texts", () => {
    const l3 = lessons[2]?.meta as Lesson;
    const mc = toClientLesson(l3).sections.find((s) => s.type === "check" && s.answerType === "multiple_choice");
    expect(mc && "choices" in mc ? mc.choices?.length : 0).toBe(4);
  });
});

describe("engine verification logic (with a fake engine)", () => {
  const fake = (equalFn: (a: string, b: string) => boolean): EngineClient => ({
    verify: async (a, b) => ({ equal: equalFn(a, b) }),
    check: async (r) => ({ status: r.student === r.correct ? "correct" : "incorrect", code: "x", message: "" }),
  });

  it("flags a worked example whose stated result is wrong", async () => {
    const l = mutated((x) => {
      const ex = x.sections.find((s) => s.type === "example");
      if (ex?.type === "example") ex.verify[0] = { expr: "(1,2)+(3,4)", equals: "(4,7)" };
    });
    const issues = await verifyLessonWithEngine(l, "t.yaml", fake((a, b) => a === b || (a === "(1,2)+(3,4)" && b === "(4,6)")));
    expect(issues.map((i) => i.message).join("\n")).toContain("is NOT equal to");
  });

  it("flags a multiple-choice question with two right options or duplicates", async () => {
    const l3 = structuredClone(lessons[2]?.meta as Lesson);
    const mc = l3.sections.find((s) => s.type === "check" && s.answerType === "multiple_choice");
    if (mc?.type !== "check") throw new Error("fixture changed");
    // pretend every option equals the answer
    const issues = await verifyLessonWithEngine(l3, "t.yaml", fake(() => true));
    const text = issues.map((i) => i.message).join("\n");
    expect(text).toContain("equals the answer but is not the marked correct option");
    expect(text).toContain("distractors must all differ");
  });

  it("flags an answer key that does not check itself", async () => {
    const engine: EngineClient = {
      verify: async () => ({ equal: true }),
      check: async () => ({ status: "invalid", code: "parse_error", message: "bad" }),
    };
    const issues = await verifyLessonWithEngine(first, "t.yaml", engine);
    expect(issues.map((i) => i.message).join("\n")).toContain("does not check itself");
  });

  it("flags a 'common mistake' that is actually the correct answer", async () => {
    const engine: EngineClient = {
      verify: async () => ({ equal: true }),
      check: async () => ({ status: "correct", code: "ok", message: "" }),
    };
    const issues = await verifyLessonWithEngine(first, "t.yaml", engine);
    expect(issues.map((i) => i.message).join("\n")).toContain("equals the correct answer");
  });
});
