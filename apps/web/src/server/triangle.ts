import { LINE_FORMS, type LineForm, type LineForms, type TriangleCircle, type TriangleData } from "@allmaths/core";
import type { TriangleCircleDto, TriangleDto } from "@/lib/triangle-types";
import { renderMath } from "./render";

const m = (latex: string): string => renderMath(latex, false);

function forms(f: LineForms): Record<LineForm, string | null> {
  const out = {} as Record<LineForm, string | null>;
  for (const key of LINE_FORMS) out[key] = f[key] === null ? null : m(f[key]);
  return out;
}

function circle(c: TriangleCircle): TriangleCircleDto {
  return {
    centerHtml: m(c.center),
    radiusHtml: m(c.radius),
    analyticHtml: m(c.analytic),
    generalHtml: m(c.general),
    parametricHtml: m(c.parametric),
    perimeterHtml: m(c.perimeter),
    areaHtml: m(c.area),
  };
}

/** Renders every formula of the engine's answer to KaTeX HTML (the browser never sees raw LaTeX). */
export function toTriangleDto(d: TriangleData): TriangleDto {
  return {
    vertices: Object.fromEntries(Object.entries(d.vertices).map(([k, v]) => [k, m(v)])),
    sides: Object.entries(d.sides).map(([key, s]) => ({ key, name: s.name, lengthHtml: m(s.length) })),
    longest: d.longest,
    shortest: d.shortest,
    perimeterHtml: m(d.perimeter),
    semiperimeterHtml: m(d.semiperimeter),
    areaHtml: m(d.area),
    kind: d.kind,
    angles: Object.entries(d.angles).map(([vertex, a]) => ({ vertex, cosHtml: m(a.cos), angleHtml: m(a.angle), degreesHtml: a.degrees === null ? null : m(a.degrees) })),
    centers: Object.fromEntries(Object.entries(d.centers).map(([k, v]) => [k, m(v)])),
    radii: { rHtml: m(d.radii.r), RHtml: m(d.radii.R) },
    euler: d.euler === null ? null : forms(d.euler),
    circles: { incircle: circle(d.circles.incircle), circumcircle: circle(d.circles.circumcircle), ninepoint: circle(d.circles.ninepoint) },
    excircles: Object.entries(d.excircles).map(([vertex, e]) => ({ vertex, centerHtml: m(e.center), radiusHtml: m(e.radius) })),
    lines: d.lines.map((l) => ({
      id: l.id,
      group: l.group,
      label: l.label,
      lengthHtml: m(l.length),
      fromHtml: m(l.from_point),
      toHtml: m(l.to_point),
      forms: forms(l.forms),
      extra: Object.fromEntries(Object.entries(l.extra).map(([k, v]) => [k, m(v)])),
    })),
    figure: d.figure,
  };
}
