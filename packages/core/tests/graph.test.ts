import { describe, expect, it } from "vitest";
import { classify, drawable, evalConstant, marchingSquares, normalizeExpr, parameterNames, sampleCurve3, sampleFunction, sampleSurface } from "../src/graph";
import { compileExpr } from "../src/plot";

const VIEW = { xmin: -6, xmax: 6, ymin: -4, ymax: 4 };

describe("reading what the learner types", () => {
  it("inserts the multiplication that is written implicitly", () => {
    expect(normalizeExpr("2x")).toBe("2*x");
    expect(normalizeExpr("x(x+1)")).toBe("x*(x+1)");
    expect(normalizeExpr("(x+1)(x-1)")).toBe("(x+1)*(x-1)");
    expect(normalizeExpr("3sin(2x)")).toBe("3*sin(2*x)");
    expect(normalizeExpr("2pi")).toBe("2*pi");
    expect(normalizeExpr("xy")).toBe("x*y");
    expect(normalizeExpr("ax^2+bx+c")).toBe("a*x^2+b*x+c");
    expect(normalizeExpr("x²")).toBe("x^2");
    expect(normalizeExpr("sin x")).toBe("sin(x)");
    expect(normalizeExpr("e^(2x)")).toBe("e^(2*x)");
    expect(normalizeExpr("√(x)")).toBe("sqrt(x)");
    // an unknown word is not turned into a product of letters: the error names it
    expect(normalizeExpr("foo(x)")).toBe("foo(x)");
    expect(normalizeExpr("sinx")).toBe("sinx");
  });

  it("the normalised text is evaluated correctly", () => {
    expect(compileExpr(normalizeExpr("2x(x+1)"), ["x"])(3)).toBe(24);
    expect(compileExpr(normalizeExpr("3sin(pi x/2)"), ["x"])(1)).toBeCloseTo(3);
  });

  it("tells what kind of object a line is", () => {
    expect(classify("y = x^2")).toMatchObject({ kind: "function", expr: "x^2" });
    expect(classify("sin(x)/x")).toMatchObject({ kind: "function" });
    expect(classify("x = y^2")).toMatchObject({ kind: "xfunction" });
    expect(classify("r = 1 + cos(theta)")).toMatchObject({ kind: "polar", expr: "1+cos(t)" });
    expect(classify("x^2 + y^2 = 4")).toMatchObject({ kind: "implicit" });
    expect(classify("(cos(t), sin(t))")).toMatchObject({ kind: "parametric", t0: "0", t1: "2*pi" });
    expect(classify("(t, t^2), t in [0, 3]")).toMatchObject({ kind: "parametric", t0: "0", t1: "3" });
    expect(classify("(2, 3)")).toMatchObject({ kind: "point" });
    expect(classify("   ")).toEqual({ kind: "empty" });
    expect(classify("1 = 2 = 3").kind).toBe("error");
    expect(classify("4 = 5").kind).toBe("error");
  });

  it("finds the sliders it needs", () => {
    expect(parameterNames([classify("y = a*x^2 + b")])).toEqual(["a", "b"]);
    expect(parameterNames([classify("k sin(x)"), classify("y = m x")])).toEqual(["k", "m"]);
    expect(parameterNames([classify("y = sin(x) + e^x"), classify("r = 1 + cos(theta)")])).toEqual([]);
  });
});

describe("sampling", () => {
  it("a smooth function is one piece, and an asymptote breaks the curve", () => {
    expect(sampleFunction(Math.sin, VIEW)).toHaveLength(1);
    expect(sampleFunction(Math.tan, VIEW).length).toBeGreaterThanOrEqual(3);
    expect(sampleFunction((x) => 1 / x, VIEW).length).toBeGreaterThanOrEqual(2);
    // where it is not defined there is no point
    const sq = sampleFunction(Math.sqrt, VIEW);
    expect(sq.flat().every(([x]) => x >= 0)).toBe(true);
  });

  it("an implicit circle is drawn on the circle", () => {
    const segs = marchingSquares((x, y) => x * x + y * y - 4, { xmin: -3, xmax: 3, ymin: -3, ymax: 3 });
    expect(segs.length).toBeGreaterThan(100);
    for (const [a, b, c, d] of segs) {
      expect(Math.hypot(a, b)).toBeCloseTo(2, 1);
      expect(Math.hypot(c, d)).toBeCloseTo(2, 1);
    }
  });

  it("two crossing lines give the two branches of the cross", () => {
    const segs = marchingSquares((x, y) => x * y, { xmin: -2, xmax: 2, ymin: -2, ymax: 2 }, 40, 40);
    expect(segs.length).toBeGreaterThan(40);
    for (const [a, b, c, d] of segs) {
      expect(Math.min(Math.abs(a), Math.abs(b))).toBeLessThan(0.06);
      expect(Math.min(Math.abs(c), Math.abs(d))).toBeLessThan(0.06);
    }
  });

  it("draws every kind of item and reports a bad one instead of failing", () => {
    expect(drawable(classify("y = a x^2"), { a: 2 }, VIEW).kind).toBe("lines");
    expect(drawable(classify("x^2+y^2=a"), { a: 4 }, VIEW).kind).toBe("segments");
    expect(drawable(classify("r = 1 + cos(theta)"), {}, VIEW).kind).toBe("lines");
    expect(drawable(classify("(cos(t), sin(t))"), {}, VIEW).kind).toBe("lines");
    expect(drawable(classify("(1, 2)"), {}, VIEW)).toEqual({ kind: "point", at: [1, 2] });
    const bad = drawable(classify("y = foo(x)"), {}, VIEW);
    expect(bad).toMatchObject({ kind: "error" });
    expect(bad.kind === "error" && bad.message).toContain("Unknown function foo");
    expect(drawable(classify("y = x +"), {}, VIEW).kind).toBe("error");
  });

  it("a slider changes the curve", () => {
    const at = (a: number) => {
      const d = drawable(classify("y = a x"), { a }, VIEW);
      return d.kind === "lines" ? d.pieces[0]![d.pieces[0]!.length - 1]![1] : NaN;
    };
    expect(at(1)).toBeCloseTo(6);
    expect(at(-0.5)).toBeCloseTo(-3);
  });
});

describe("constants", () => {
  it("evaluates the ends of a range", () => {
    expect(evalConstant("2pi")).toBeCloseTo(2 * Math.PI);
    expect(evalConstant("a+1", { a: 2 })).toBe(3);
    expect(() => evalConstant("1/0")).toThrow();
  });
});

describe("space", () => {
  it("samples a surface and leaves holes where it is not defined", () => {
    const g = sampleSurface("x y", {}, [-2, 2], [-2, 2], 4);
    expect(g).toHaveLength(5);
    expect(g[0]![0]).toEqual([-2, -2, 4]);
    expect(g[4]![4]).toEqual([2, 2, 4]);
    const holes = sampleSurface("ln(x)", {}, [-1, 1], [0, 1], 4);
    expect(holes[0]![0]).toBeNull();
    expect(holes[0]![4]).not.toBeNull();
  });

  it("samples a space curve", () => {
    const pts = sampleCurve3("cos(t)", "sin(t)", "t", {}, 0, 2 * Math.PI, 8);
    expect(pts).toHaveLength(9);
    expect(pts[0]).toEqual([1, 0, 0]);
    expect(pts[8]![2]).toBeCloseTo(2 * Math.PI);
  });
});
