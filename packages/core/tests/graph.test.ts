import { describe, expect, it } from "vitest";
import { classify, drawable, evalConstant, marchingSquares, normalizeExpr, parameterNames, sampleCurve3, sampleFunction, sampleSurface, specialPoints, namedPoints, measure, pointAtPlace, pointPositions, rejectDuplicatePoints } from "../src/graph";
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

describe("inequalities", () => {
  it("reads <, >, <= and >= (and the printed signs)", () => {
    expect(classify("y > x^2")).toMatchObject({ kind: "region", op: ">" });
    expect(classify("x^2 + y^2 ≤ 4")).toMatchObject({ kind: "region", op: "<=" });
    expect(classify("y >= 2x")).toMatchObject({ kind: "region", lhs: "y", rhs: "2*x" });
    expect(classify("3 < 4")).toMatchObject({ kind: "error" });
    expect(classify("y < x < 3")).toMatchObject({ kind: "error" });
  });
  it("says which points are inside, and whether the boundary is included", () => {
    const d = drawable(classify("x^2 + y^2 <= 4"), {}, VIEW);
    if (d.kind !== "region") throw new Error("expected a region");
    expect(d.inside(0, 0)).toBe(true);
    expect(d.inside(2, 0)).toBe(true);
    expect(d.inside(2.1, 0)).toBe(false);
    expect(d.strict).toBe(false);
    expect(d.boundary.length).toBeGreaterThan(20);
    const s = drawable(classify("y > x"), {}, VIEW);
    if (s.kind !== "region") throw new Error("expected a region");
    expect(s.inside(1, 1)).toBe(false);
    expect(s.inside(0, 1)).toBe(true);
    expect(s.strict).toBe(true);
  });
  it("makes a slider from a letter", () => {
    expect(parameterNames([classify("y < a*x + 1")])).toEqual(["a"]);
  });
});

describe("roots and intersections", () => {
  const near = (v: number, w: number) => Math.abs(v - w) < 1e-6;
  it("finds the roots of x^2 - 4", () => {
    const roots = specialPoints([classify("y = x^2 - 4")], {}, VIEW).map((p) => p.at[0]).sort((a, b) => a - b);
    expect(roots).toHaveLength(2);
    expect(near(roots[0]!, -2) && near(roots[1]!, 2)).toBe(true);
  });
  it("finds where two lines meet, once, even when it is also a root", () => {
    const pts = specialPoints([classify("y = x^2 - 4"), classify("y = x - 2")], {}, VIEW);
    const meet = pts.filter((p) => p.kind === "intersection").sort((a, b) => a.at[0] - b.at[0]);
    expect(meet).toHaveLength(2);
    expect(near(meet[0]!.at[0], -1) && near(meet[0]!.at[1], -3)).toBe(true);
    expect(near(meet[1]!.at[0], 2) && near(meet[1]!.at[1], 0)).toBe(true);
    expect(meet[1]!.lines).toEqual([1, 2]);
    expect(pts).toHaveLength(3); // the root -2 and the two meeting points
  });
  it("does not take the jump of tan(x) or 1/x for a zero", () => {
    const pts = specialPoints([classify("y = 1/x")], {}, VIEW);
    expect(pts).toEqual([]);
  });
  it("uses the sliders", () => {
    const pts = specialPoints([classify("y = x - a")], { a: 3 }, VIEW);
    expect(pts).toHaveLength(1);
    expect(near(pts[0]!.at[0], 3)).toBe(true);
  });
});

describe("named points, segments and lines", () => {
  it("reads P(2,2), A = (1, 2) and segment(A, B), but still reads f(x) and sin(x) as functions", () => {
    expect(classify("P(2,2)")).toMatchObject({ kind: "point", name: "P", x: "2", y: "2" });
    expect(classify("A = (1, -2.5)")).toMatchObject({ kind: "point", name: "A", x: "1" });
    expect(classify("Segment(A, B)")).toMatchObject({ kind: "segment", a: "A", b: "B", mode: "segment" });
    expect(classify("line(A,B)")).toMatchObject({ kind: "segment", mode: "line" });
    expect(classify("sin(x)")).toMatchObject({ kind: "function" });
    expect(classify("P(1,2,3)")).toMatchObject({ kind: "error" });
    expect(classify("(2, 3)")).toMatchObject({ kind: "point" });
  });
  it("draws a segment between named points, and explains a missing point", () => {
    const items = [classify("A(0,0)"), classify("B(3,4)"), classify("segment(A,B)"), classify("segment(A,C)")];
    const pts = namedPoints(items, {});
    expect(pts).toEqual({ A: [0, 0], B: [3, 4] });
    const d = drawable(items[2]!, {}, VIEW, pts);
    expect(d).toEqual({ kind: "lines", pieces: [[[0, 0], [3, 4]]] });
    const bad = drawable(items[3]!, {}, VIEW, pts);
    expect(bad).toMatchObject({ kind: "error" });
    if (bad.kind === "error") expect(bad.message).toContain("C");
  });
  it("uses sliders in the coordinates of a point", () => {
    const items = [classify("P(a, 2)")];
    expect(parameterNames(items)).toEqual(["a"]);
    expect(namedPoints(items, { a: 3 })).toEqual({ P: [3, 2] });
  });
  it("measures exactly: length, midpoint and equation", () => {
    expect(measure([0, 0], [3, 4])).toEqual({ length: "5", midpoint: "(3/2, 2)", equation: "y = (4/3)x", exact: true });
    expect(measure([1, 1], [3, 2]).length).toBe("√5");
    expect(measure([0, 0], [2, 2]).length).toBe("2√2");
    expect(measure([0, 0], [1, 1]).length).toBe("√2");
    expect(measure([0, 0], [1, 2]).equation).toBe("y = 2x");
    expect(measure([0, 1], [2, 1]).equation).toBe("y = 1");
    expect(measure([2, 0], [2, 5]).equation).toBe("x = 2");
    expect(measure([0, 0], [1, 1]).equation).toBe("y = x");
    expect(measure([0, 2], [1, 1]).equation).toBe("y = -x + 2");
    expect(measure([1, 0], [3, 3]).equation).toBe("y = (3/2)x - 3/2");
    expect(measure([0, 0], [0.5, 1.5]).length).toBe("√10/2");
    expect(measure([0, 0], [1 / 3, 1]).exact).toBe(false);
  });
});

describe("circles, polygons and differential equations", () => {
  it("reads circle(A, B), polygon(A, B, C), y' = f and ode(y' = f, A)", () => {
    expect(classify("circle(A, B)")).toMatchObject({ kind: "circle", center: "A", through: "B" });
    expect(classify("Polygon(A, B, C, D)")).toMatchObject({ kind: "polygon", names: ["A", "B", "C", "D"] });
    expect(classify("polygon(A, B)")).toMatchObject({ kind: "error" });
    expect(classify("y' = x - y")).toMatchObject({ kind: "slopefield", expr: "x-y" });
    expect(classify("dy/dx = 2x")).toMatchObject({ kind: "slopefield", expr: "2*x" });
    expect(classify("ode(y' = x - y, A)")).toMatchObject({ kind: "slopefield", expr: "x-y", at: "A" });
  });
  it("draws a circle and a polygon from named points, and a solution curve through a point", () => {
    const items = [classify("A(0, 0)"), classify("B(3, 4)"), classify("C(6, 0)"), classify("circle(A, B)"), classify("polygon(A, B, C)"), classify("ode(y' = y, D)"), classify("circle(A, Q)"), classify("D(0, 1)")];
    const pts = namedPoints(items, {});
    const c = drawable(items[3]!, {}, VIEW, pts);
    expect(c.kind).toBe("lines");
    const p = drawable(items[4]!, {}, VIEW, pts);
    expect(p).toEqual({ kind: "polygon", pts: [[0, 0], [3, 4], [6, 0]] });
    const o = drawable(items[5]!, {}, VIEW, pts);
    if (o.kind !== "slopefield") throw new Error("expected a slope field");
    expect(o.f(1, 2)).toBe(2);
    const at = (x: number) => o.curve[0]!.reduce((b, q) => (Math.abs(q[0] - x) < Math.abs(b[0] - x) ? q : b))[1];
    expect(at(1)).toBeCloseTo(Math.E, 2);
    expect(drawable(items[6]!, {}, VIEW, pts)).toMatchObject({ kind: "error" });
  });
  it("uses sliders in a slope field", () => {
    expect(parameterNames([classify("y' = a*y")])).toEqual(["a"]);
  });
});

describe("two points cannot be in the same place or have the same name", () => {
  const read = (...rows: string[]) => rows.map(classify);
  const message = (item: ReturnType<typeof classify> | undefined) => (item && item.kind === "error" ? item.message : "");

  it("keeps the first point and rejects a later point at the same coordinates, saying where the other one is", () => {
    const items = rejectDuplicatePoints(read("G = (5, -2)", "H = (4, -2)", "I = (4, -2)"), {});
    expect(items.map((i) => i.kind)).toEqual(["point", "point", "error"]);
    expect(message(items[2])).toBe("The point H is already at (4, -2). Two points cannot be in the same place.");
  });

  it("compares unnamed points too, and a named one with an unnamed one", () => {
    const items = rejectDuplicatePoints(read("(1, 2)", "(1, 2)", "A = (1, 2)", "B = (2, 1)"), {});
    expect(items.map((i) => i.kind)).toEqual(["point", "error", "error", "point"]);
    expect(message(items[1])).toBe("A point is already at (1, 2). Two points cannot be in the same place.");
    expect(message(items[2])).toBe("A point is already at (1, 2). Two points cannot be in the same place.");
  });

  it("sees that the same position written differently is the same position", () => {
    const items = rejectDuplicatePoints(read("A = (0.3, 1)", "B = (0.1 + 0.2, 2/2)", "C = (3/10, 1)"), {});
    expect(items.map((i) => i.kind)).toEqual(["point", "error", "error"]);
  });

  it("rejects a name that is used twice, even at different places", () => {
    const items = rejectDuplicatePoints(read("A = (1, 2)", "A = (3, 4)"), {});
    expect(items.map((i) => i.kind)).toEqual(["point", "error"]);
    expect(message(items[1])).toBe("The name A is already used by another point. Choose another letter.");
  });

  it("a rejected point is not available to the segments, so nothing is drawn through a point that is not there", () => {
    const items = rejectDuplicatePoints(read("A = (1, 2)", "B = (1, 2)", "segment(A, B)"), {});
    const points = namedPoints(items, {});
    expect(Object.keys(points)).toEqual(["A"]);
    expect(drawable(items[2]!, {}, VIEW, points)).toMatchObject({ kind: "error", message: expect.stringContaining("The point B is not defined") });
  });

  it("does not compare a point that moves with a slider (it can cross another point without being refused)", () => {
    const items = rejectDuplicatePoints(read("Q = (1, 2)", "P = (a, 2)"), { a: 1 });
    expect(items.map((i) => i.kind)).toEqual(["point", "point"]);
  });

  it("ignores rows that are empty or hidden (the page turns a hidden row into an empty one)", () => {
    const items = rejectDuplicatePoints([classify("A = (1, 2)"), { kind: "empty" }, classify("B = (1, 2)")], {});
    expect(items.map((i) => i.kind)).toEqual(["point", "empty", "error"]);
    const afterHide = rejectDuplicatePoints([{ kind: "empty" }, classify("B = (1, 2)")], {});
    expect(afterHide.map((i) => i.kind)).toEqual(["empty", "point"]);
  });

  it("finds the point that is at a place, leaving out the point that is being moved", () => {
    const items = read("A = (1, 2)", "B = (3, 4)");
    expect(pointAtPlace(items, {}, [3, 4])).toMatchObject({ index: 1, name: "B" });
    expect(pointAtPlace(items, {}, [3, 4], 1)).toBeUndefined();
    expect(pointAtPlace(items, {}, [9, 9])).toBeUndefined();
    expect(pointPositions(items, {}).map((p) => p.at)).toEqual([[1, 2], [3, 4]]);
  });
});

describe("what a learner types that the grapher used to refuse", () => {
  const value = (src: string, x = 0) => compileExpr(normalizeExpr(src), ["x"])(x);

  it("reads floor, ceil, round, sign, cbrt, sec, csc, cot, log10 and log2", () => {
    expect(value("floor(x)", 2.7)).toBe(2);
    expect(value("ceil(x)", 2.1)).toBe(3);
    expect(value("round(x)", 2.6)).toBe(3);
    expect(value("sign(x)", -3)).toBe(-1);
    expect(value("cbrt(x)", -8)).toBe(-2);
    expect(value("sec(x)", 0)).toBeCloseTo(1, 12);
    expect(value("csc(x)", Math.PI / 2)).toBeCloseTo(1, 12);
    expect(value("cot(x)", Math.PI / 4)).toBeCloseTo(1, 12);
    expect(value("log10(x)", 1000)).toBeCloseTo(3, 12);
    expect(value("log2(x)", 8)).toBeCloseTo(3, 12);
    expect(value("log(x)", Math.E)).toBeCloseTo(1, 12); // log is still the natural logarithm, as on the rest of the platform
    expect(value("2log10(x)", 100)).toBeCloseTo(4, 12);
  });

  it("draws them (a curve, not an error)", () => {
    for (const row of ["y = sec(x)", "y = cot(x)", "y = floor(x)", "y = sign(x)", "y = log10(x)", "y = cbrt(x)"]) {
      expect(drawable(classify(row), {}, VIEW, {})).toMatchObject({ kind: "lines" });
    }
  });

  it("takes y = expression with y on both sides for an implicit curve, not a function that cannot be read", () => {
    expect(classify("y = x^2 y")).toEqual({ kind: "implicit", lhs: "y", rhs: "x^2*y" });
    expect(classify("y = x^2")).toMatchObject({ kind: "function" });
    expect(drawable(classify("y = x^2 y"), {}, VIEW, {})).toMatchObject({ kind: "segments" });
  });

  it("says that a point needs a capital letter", () => {
    expect(classify("a = (1, 2)")).toEqual({ kind: "error", message: "Name a point with a capital letter, for example A = (1, 2)." });
    expect(classify("A = (1, 2)")).toMatchObject({ kind: "point", name: "A" });
  });
});
