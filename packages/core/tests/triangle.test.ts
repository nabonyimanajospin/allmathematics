import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { LINE_FORMS, LINE_GROUPS, triangleResponseSchema } from "../src";

/**
 * The fixtures are real answers of the engine (regenerate them with analyze() of apps/math-engine/allmaths_engine/triangle.py):
 * the schema is the contract between the engine and the website, so a change of format on either side fails here.
 */
function load(name: string): unknown {
  return JSON.parse(readFileSync(new URL(`./fixtures/${name}.json`, import.meta.url), "utf-8"));
}

describe.each(["triangle-345", "triangle-notes"])("the engine answer %s", (name) => {
  const parsed = triangleResponseSchema.safeParse(load(name));

  it("matches the schema", () => {
    expect(parsed.success).toBe(true);
  });

  it("has fifteen lines, three of each kind, each with its eight forms", () => {
    const data = parsed.data?.data;
    expect(data?.lines).toHaveLength(15);
    for (const group of LINE_GROUPS) expect(data?.lines.filter((l) => l.group === group)).toHaveLength(3);
    for (const line of data?.lines ?? []) {
      for (const form of LINE_FORMS) expect(line.forms).toHaveProperty(form);
    }
  });

  it("never contains a decimal number in a result", () => {
    const data = parsed.data?.data;
    const text = JSON.stringify({ ...data, figure: undefined });
    // (the row spacing of a column vector, written [0.7em], is layout and not a result)
    expect(text.replaceAll("[0.7em]", "")).not.toMatch(/\d\.\d/);
  });
});

describe("the 3-4-5 triangle", () => {
  const data = triangleResponseSchema.parse(load("triangle-345")).data;
  it("has exact sides, area and centers", () => {
    expect(data?.sides.a?.length).toBe("5");
    expect(data?.area).toBe("6");
    expect(data?.radii).toEqual({ r: "1", R: "\\dfrac{5}{2}" });
    expect(data?.kind).toEqual({ by_sides: "scalene", by_angles: "right" });
  });
});

describe("a bad answer", () => {
  it("is accepted without data", () => {
    const parsed = triangleResponseSchema.parse({ ok: false, code: "collinear", message: "The three points are on one straight line." });
    expect(parsed.ok).toBe(false);
    expect(parsed.data).toBeUndefined();
  });
});
