import { describe, expect, it } from "vitest";
import { pointTable, project3, validateFigure, type Figure } from "../src";

const tri: Figure = {
  dim: 2,
  alt: "A triangle with three labelled vertices.",
  view: [-2, 16, -2, 14],
  items: [
    { t: "point", id: "A", at: [0, 0] },
    { t: "point", id: "B", at: [14, 0] },
    { t: "point", id: "C", at: ["19/3", 4] },
    { t: "polygon", pts: ["A", "B", "C"] },
    { t: "line", through: ["A", [5, 12]] },
  ],
};

describe("figure", () => {
  it("reads exact coordinates such as fractions and radicals", () => {
    expect(validateFigure(tri)).toBeNull();
    expect(pointTable(tri).get("C")![0]).toBeCloseTo(19 / 3, 12);
    const withRoot: Figure = { ...tri, items: [{ t: "point", id: "P", at: ["sqrt(2)", 1] }] };
    expect(pointTable(withRoot).get("P")![0]).toBeCloseTo(Math.SQRT2, 12);
  });

  it("reports an unknown point, a duplicate id, a wrong number of coordinates and a bad number", () => {
    expect(validateFigure({ ...tri, items: [...tri.items, { t: "segment", from: "A", to: "Z" }] })).toMatch(/unknown point Z/);
    expect(validateFigure({ ...tri, items: [...tri.items, { t: "point", id: "A", at: [1, 1] }] })).toMatch(/used twice/);
    expect(validateFigure({ ...tri, items: [{ t: "point", id: "Q", at: [1, 2, 3] }] })).toMatch(/needs 2 coordinates/);
    expect(validateFigure({ ...tri, items: [{ t: "point", id: "Q", at: ["abc", 2] }] })).toMatch(/cannot read the coordinate/);
    expect(validateFigure({ ...tri, view: [1, 2] })).toMatch(/view/);
  });

  it("a 3D figure rejects an unbounded line and projects points with an orthographic rotation", () => {
    const cube: Figure = { dim: 3, alt: "A point in space with the axes.", view: [5], items: [{ t: "point", id: "P", at: [1, 2, 3] }] };
    expect(validateFigure(cube)).toBeNull();
    expect(validateFigure({ ...cube, items: [...cube.items, { t: "line", through: ["P", [0, 0, 0]] }] })).toMatch(/2D/);
    // looking straight along the y axis (yaw 0, pitch 0): screen x = x, screen y = z
    const q = project3([1, 2, 3], 0, 0);
    expect(q.x).toBeCloseTo(1, 12);
    expect(q.y).toBeCloseTo(3, 12);
    // a rotation never changes the distance from the origin
    const r = project3([1, 2, 3], 0.7, 0.4);
    expect(Math.hypot(r.x, r.y, r.depth)).toBeCloseTo(Math.hypot(1, 2, 3), 10);
  });
});
