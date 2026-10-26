import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { LINE_FORMS, triangleResponseSchema } from "@allmaths/core";
import { toTriangleDto } from "../src/server/triangle";

/** The fixtures are real answers of the math engine (see packages/core/tests/triangle.test.ts). */
function load(name: string) {
  const raw = readFileSync(new URL(`../../../packages/core/tests/fixtures/${name}.json`, import.meta.url), "utf-8");
  const parsed = triangleResponseSchema.parse(JSON.parse(raw));
  if (!parsed.data) throw new Error("the fixture has no data");
  return parsed.data;
}

/** Every string of the DTO that holds a formula (the ones ending in Html, and the maps of formulas). */
function formulas(dto: ReturnType<typeof toTriangleDto>): string[] {
  const out: string[] = [];
  const walk = (v: unknown, key = ""): void => {
    if (typeof v === "string") {
      if (key.endsWith("Html") || key === "intercept" || LINE_FORMS.includes(key as (typeof LINE_FORMS)[number])) out.push(v);
    } else if (Array.isArray(v)) v.forEach((x) => walk(x, key));
    else if (v && typeof v === "object" && key !== "figure") for (const [k, x] of Object.entries(v)) walk(x, k);
  };
  walk(dto);
  return out;
}

describe("toTriangleDto", () => {
  for (const name of ["triangle-345", "triangle-notes"]) {
    const dto = toTriangleDto(load(name));

    it(`${name}: every formula is rendered to KaTeX HTML and no raw LaTeX reaches the browser`, () => {
      const all = formulas(dto);
      expect(all.length).toBeGreaterThan(150);
      for (const html of all) {
        expect(html).toContain('class="katex"');
        // KaTeX keeps the source in a MathML annotation (for screen readers); outside it no command may be left
        const visible = html.replace(/<annotation[\s\S]*?<\/annotation>/g, "");
        expect(visible).not.toMatch(/\\(dfrac|tfrac|frac|sqrt|left|right|begin)/);
      }
    });

    it(`${name}: keeps the structure: 15 lines with eight forms, three angles, three sides`, () => {
      expect(dto.lines).toHaveLength(15);
      expect(dto.angles.map((a) => a.vertex)).toEqual(["A", "B", "C"]);
      expect(dto.sides.map((s) => s.name)).toEqual(["BC", "CA", "AB"]);
      for (const line of dto.lines) expect(Object.keys(line.forms)).toEqual([...LINE_FORMS]);
    });
  }

  it("a form that does not exist stays null (a vertical line has no intercept form)", () => {
    const dto = toTriangleDto(load("triangle-345"));
    const vertical = dto.lines.find((l) => l.id === "side-AB");
    expect(vertical?.forms.intercept).toBeNull();
    expect(dto.lines.find((l) => l.id === "side-BC")?.forms.intercept).not.toBeNull();
  });
});
