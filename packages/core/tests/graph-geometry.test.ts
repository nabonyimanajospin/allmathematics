import { describe, expect, it } from "vitest";
import { circlePoints, measureCircle, measurePolygon, parseParamSurface, sampleParamSurface, slopeFunction, solutionCurve } from "../src/graph-geometry";

describe("measuring a circle exactly", () => {
  it("gives radius, circumference, area and equation as exact values", () => {
    const m = measureCircle([0, 0], [3, 4]);
    expect(m.exact).toBe(true);
    expect(Object.fromEntries(m.lines.map((l) => [l.label, l.value]))).toEqual({ radius: "5", circumference: "10π", area: "25π", equation: "x² + y² = 25" });
  });
  it("keeps a radical radius and writes shifted centres", () => {
    const m = measureCircle([1, -2], [2, 0]); // r^2 = 1 + 4 = 5
    const v = Object.fromEntries(m.lines.map((l) => [l.label, l.value]));
    expect(v.radius).toBe("√5");
    expect(v.area).toBe("5π");
    expect(v.equation).toBe("(x - 1)² + (y + 2)² = 5");
    expect(v.circumference).toBe("2√5π");
  });
  it("is approximate (and says so) when a coordinate is not a simple decimal", () => {
    expect(measureCircle([0, 0], [1 / 3, 0]).exact).toBe(false);
  });
  it("draws a closed curve at the right distance", () => {
    const pts = circlePoints([1, 1], [4, 5], 100);
    expect(pts[0]![0]).toBeCloseTo(pts[100]![0], 9);
    expect(pts[0]![1]).toBeCloseTo(pts[100]![1], 9);
    for (const [x, y] of pts) expect(Math.hypot(x - 1, y - 1)).toBeCloseTo(5, 9);
  });
});

describe("measuring a polygon exactly", () => {
  it("a rectangle: perimeter and area", () => {
    const m = measurePolygon([[0, 0], [4, 0], [4, 3], [0, 3]]);
    expect(Object.fromEntries(m.lines.map((l) => [l.label, l.value]))).toEqual({ perimeter: "14", area: "12" });
  });
  it("a triangle with radical sides: like radicals are gathered", () => {
    const m = measurePolygon([[0, 0], [1, 1], [2, 0]]); // sides sqrt2, sqrt2, 2; area 1
    const v = Object.fromEntries(m.lines.map((l) => [l.label, l.value]));
    expect(v.area).toBe("1");
    expect(v.perimeter).toBe("2 + 2√2");
  });
  it("the area does not depend on the direction of the vertices", () => {
    const a = measurePolygon([[0, 0], [4, 0], [0, 3]]).lines.find((l) => l.label === "area")!.value;
    const b = measurePolygon([[0, 0], [0, 3], [4, 0]]).lines.find((l) => l.label === "area")!.value;
    expect(a).toBe("6");
    expect(b).toBe("6");
  });
  it("fractions are exact", () => {
    const m = measurePolygon([[0, 0], [1.5, 0], [0, 1]]);
    expect(m.lines.find((l) => l.label === "area")!.value).toBe("3/4");
  });
});

describe("slope fields and solution curves", () => {
  it("y' = y has the solution y = e^x through (0, 1)", () => {
    const f = slopeFunction("y", {});
    const [curve] = solutionCurve(f, 0, 1, -2, 2, 1e6);
    const at = (x: number) => curve!.reduce((best, p) => (Math.abs(p[0] - x) < Math.abs(best[0] - x) ? p : best))[1];
    expect(at(1)).toBeCloseTo(Math.E, 3);
    expect(at(-1)).toBeCloseTo(Math.exp(-1), 3);
  });
  it("y' = x - y has the solution y = x - 1 + 2e^{-x} through (0, 1)", () => {
    const f = slopeFunction("x - y", {});
    const [curve] = solutionCurve(f, 0, 1, -3, 3, 1e6);
    for (const p of curve!) expect(p[1]).toBeCloseTo(p[0] - 1 + 2 * Math.exp(-p[0]), 5);
  });
  it("stops where the solution blows up", () => {
    const f = slopeFunction("y^2", {}); // y = 1/(1 - x) through (0, 1) blows up at x = 1
    const [curve] = solutionCurve(f, 0, 1, -2, 2, 1e3);
    expect(Math.max(...curve!.map((p) => p[0]))).toBeLessThan(1.001);
  });
});

describe("parametric surfaces", () => {
  it("reads the three coordinates and the ranges", () => {
    const s = parseParamSurface("(3*sin(u)*cos(v), 3*sin(u)*sin(v), 3*cos(u)), u in [0, pi], v in [0, 2*pi]");
    expect(s).toEqual({ x: "3*sin(u)*cos(v)", y: "3*sin(u)*sin(v)", z: "3*cos(u)", u: ["0", "pi"], v: ["0", "2*pi"] });
    expect(parseParamSurface("(u, v, u*v)")).toMatchObject({ u: ["0", "2*pi"], v: ["0", "2*pi"] });
    expect(parseParamSurface("(1, 2, 3)")).toBeNull(); // no u or v: not a surface
    expect(parseParamSurface("z = x*y")).toBeNull();
  });
  it("samples a sphere: every point is at distance 3 from the origin", () => {
    const s = parseParamSurface("(3*sin(u)*cos(v), 3*sin(u)*sin(v), 3*cos(u)), u in [0, pi], v in [0, 2*pi]")!;
    const num = (t: string) => (t === "pi" ? Math.PI : t === "2*pi" ? 2 * Math.PI : Number(t));
    const grid = sampleParamSurface(s, {}, num, 20);
    expect(grid).toHaveLength(21);
    for (const row of grid) for (const p of row) expect(Math.hypot(...p!)).toBeCloseTo(3, 9);
  });
});
