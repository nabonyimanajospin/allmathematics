/**
 * The result of the engine's triangle analysis (apps/math-engine/allmaths_engine/triangle.py): exact values as LaTeX strings,
 * plus plain drawing coordinates in `figure`. The schema is the contract between the engine and the website.
 */

import { z } from "zod";

const latex = z.string();
const xy = z.tuple([z.number(), z.number()]);

export const LINE_FORMS = ["vector", "parametric", "symmetric", "implicit", "explicit", "normal", "polar", "intercept"] as const;
export type LineForm = (typeof LINE_FORMS)[number];
export const LINE_GROUPS = ["side", "median", "altitude", "bisector", "perpbisector"] as const;
export type LineGroup = (typeof LINE_GROUPS)[number];

/** The eight equations of one line. The intercept form does not exist for a line parallel to an axis or through the origin. */
export const lineFormsSchema = z.strictObject({
  vector: latex,
  parametric: latex,
  symmetric: latex,
  implicit: latex,
  explicit: latex,
  normal: latex,
  polar: latex,
  intercept: latex.nullable(),
});
export type LineForms = z.infer<typeof lineFormsSchema>;

export const triangleLineSchema = z.strictObject({
  id: z.string(),
  group: z.enum(LINE_GROUPS),
  label: z.string(),
  length: latex,
  from_point: latex,
  to_point: latex,
  forms: lineFormsSchema,
  extra: z.record(z.string(), latex),
});
export type TriangleLine = z.infer<typeof triangleLineSchema>;

export const circleSchema = z.strictObject({
  center: latex,
  radius: latex,
  analytic: latex,
  general: latex,
  parametric: latex,
  perimeter: latex,
  area: latex,
});
export type TriangleCircle = z.infer<typeof circleSchema>;

export const triangleDataSchema = z.strictObject({
  vertices: z.record(z.string(), latex),
  sides: z.record(z.string(), z.strictObject({ name: z.string(), length: latex })),
  longest: z.array(z.string()),
  shortest: z.array(z.string()),
  perimeter: latex,
  semiperimeter: latex,
  area: latex,
  kind: z.strictObject({ by_sides: z.enum(["scalene", "isosceles", "equilateral"]), by_angles: z.enum(["acute", "right", "obtuse"]) }),
  angles: z.record(z.string(), z.strictObject({ cos: latex, angle: latex, degrees: latex.nullable() })),
  centers: z.record(z.string(), latex),
  radii: z.strictObject({ r: latex, R: latex }),
  euler: lineFormsSchema.nullable(),
  circles: z.strictObject({ incircle: circleSchema, circumcircle: circleSchema, ninepoint: circleSchema }),
  excircles: z.record(z.string(), z.strictObject({ center: latex, radius: latex })),
  lines: z.array(triangleLineSchema),
  figure: z.strictObject({
    view: z.tuple([z.number(), z.number(), z.number(), z.number()]),
    points: z.record(z.string(), xy),
    incircle: z.strictObject({ center: xy, r: z.number() }),
    circumcircle: z.strictObject({ center: xy, r: z.number() }),
  }),
});
export type TriangleData = z.infer<typeof triangleDataSchema>;

export const triangleResponseSchema = z.object({
  ok: z.boolean(),
  data: triangleDataSchema.nullable().optional(),
  code: z.string().nullable().optional(),
  message: z.string().nullable().optional(),
});
export type TriangleResponse = z.infer<typeof triangleResponseSchema>;
