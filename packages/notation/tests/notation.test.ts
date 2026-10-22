import { describe, expect, it } from "vitest";
import { extractMath, getMacros, latexPreamble, lintAnswerExpression, lintMath, lintText } from "../src";

const rules = (latex: string, opts?: { allowDecimal?: boolean; display?: boolean }) =>
  lintMath(latex, opts).map((i) => i.rule);

describe("macros", () => {
  it("defines the product macros of the course convention", () => {
    const m = getMacros("course");
    expect(m["\\dotp"]).toContain("\\langle");
    expect(m["\\crossp"]).toContain("\\left[");
    expect(m["\\boxp"]).toContain("\\langle");
  });

  it("switches convention globally", () => {
    const m = getMacros("standard");
    expect(m["\\dotp"]).toBe("#1\\cdot #2");
    expect(m["\\crossp"]).toBe("#1\\times #2");
    expect(m["\\boxp"]).toContain("\\left[");
  });

  it("every macro has balanced braces and consistent argument numbers", () => {
    for (const style of ["course", "standard"] as const) {
      for (const [name, body] of Object.entries(getMacros(style))) {
        let depth = 0;
        for (const ch of body) {
          if (ch === "{") depth++;
          if (ch === "}") depth--;
          expect(depth, `${name} in ${style}`).toBeGreaterThanOrEqual(0);
        }
        expect(depth, `${name} in ${style}`).toBe(0);
      }
    }
  });

  it("generates a LaTeX preamble with argument counts", () => {
    const p = latexPreamble("course");
    expect(p).toContain("\\newcommand{\\dotp}[2]");
    expect(p).toContain("\\newcommand{\\boxp}[3]");
    expect(p).toContain("\\newcommand{\\R}{");
  });
});

describe("lint: vectors", () => {
  it("accepts correct notation", () => {
    expect(rules("\\dotp{\\vec u}{\\vec v}=-8")).toEqual([]);
    expect(rules("\\crossp{\\vec u}{\\vec v}=(-10,7,9)")).toEqual([]);
    expect(rules("\\boxp{\\vec u}{\\vec v}{\\vec w}=16")).toEqual([]);
    expect(rules("\\norm{\\vec u}=\\sqrt{14}")).toEqual([]);
    expect(rules("\\dotp{(2,-1,3)}{(1,4,-2)}")).toEqual([]);
    expect(rules("\\dotp{\\vecab{A}{B}}{\\vecab{A}{C}}")).toEqual([]);
  });

  it("flags \\cdot and \\times between vectors", () => {
    expect(rules("\\vec u \\cdot \\vec v")).toContain("vector-dot-uses-cdot");
    expect(rules("\\vec u \\times \\vec v")).toContain("vector-cross-uses-times");
    expect(rules("\\overrightarrow{AB}\\times\\overrightarrow{AC}")).toContain("vector-cross-uses-times");
  });

  it("does not flag scalar products", () => {
    expect(rules("2\\cdot 3=6")).toEqual([]);
    expect(rules("\\lambda\\cdot\\vec u")).toContain("vector-dot-uses-cdot"); // scalar*vector must be written \lambda\vec u
    expect(rules("\\lambda\\vec u")).toEqual([]);
  });

  it("flags plain-letter vectors inside product macros", () => {
    expect(rules("\\dotp{u}{v}")).toContain("vector-without-arrow");
    expect(rules("\\crossp{\\vec u}{v}")).toContain("vector-without-arrow");
    expect(rules("\\boxp{\\vec u}{\\vec v}{w}")).toContain("vector-without-arrow");
  });

  it("flags bold vectors and raw angle brackets", () => {
    expect(rules("\\mathbf{u}")).toContain("vector-bold");
    expect(rules("\\langle \\vec u,\\vec v\\rangle")).toContain("raw-angle-brackets");
    expect(rules("\\left\\langle a,b\\right\\rangle")).toContain("raw-angle-brackets");
  });
});

describe("lint: exact values", () => {
  it("flags decimals unless allowed", () => {
    expect(rules("x=3.5")).toContain("decimal-in-math");
    expect(rules("x=3.5", { allowDecimal: true })).toEqual([]);
    expect(rules("x_{1}=2")).toEqual([]);
  });

  it("flags unrationalized denominators", () => {
    expect(rules("\\dfrac{1}{\\sqrt{2}}")).toContain("unrationalized-denominator");
    expect(rules("\\dfrac{\\sqrt{2}}{2}")).toEqual([]);
  });

  it("warns on \\frac in display math", () => {
    const issues = lintMath("\\frac{1}{2}", { display: true });
    expect(issues.map((i) => [i.rule, i.severity])).toEqual([["display-frac-not-dfrac", "warning"]]);
  });

  it("lints answer expressions", () => {
    expect(lintAnswerExpression("19*sqrt(35)/35")).toEqual([]);
    expect(lintAnswerExpression("19/sqrt(35)").map((i) => i.rule)).toEqual(["unrationalized-denominator"]);
    expect(lintAnswerExpression("3.5").map((i) => i.rule)).toEqual(["decimal-in-math"]);
    expect(lintAnswerExpression("abs(dot(a,b))/norm(c)")).toEqual([]);
    expect(lintAnswerExpression("x/sqrt(x^2+y^2)")).toEqual([]); // a radical of an expression with letters is fine
  });
});

describe("extractMath", () => {
  it("finds inline and display math and ignores escaped dollars", () => {
    const { segments, unbalanced } = extractMath("Cost \\$5 and $x^2$ then $$\\dfrac{a}{b}$$ done");
    expect(unbalanced).toBe(false);
    expect(segments).toEqual([
      { latex: "x^2", display: false },
      { latex: "\\dfrac{a}{b}", display: true },
    ]);
  });

  it("reports unbalanced math", () => {
    expect(extractMath("an $open formula").unbalanced).toBe(true);
  });

  it("lintText finds issues only in math", () => {
    expect(lintText("Version 2.5 of the text, with $x=1$").length).toBe(0);
    expect(lintText("so $x=1.5$").map((i) => i.rule)).toEqual(["decimal-in-math"]);
  });
});
