import type { LineForm, LineGroup, TriangleData } from "@allmaths/core";

/** What the browser receives from /api/triangle: every formula is KaTeX HTML rendered on the server (suffix Html). */
export interface TriangleLineDto {
  id: string;
  group: LineGroup;
  label: string;
  lengthHtml: string;
  fromHtml: string;
  toHtml: string;
  /** The eight equations; the intercept form is null for a line parallel to an axis or through the origin. */
  forms: Record<LineForm, string | null>;
  extra: Record<string, string>;
}

export interface TriangleCircleDto {
  centerHtml: string;
  radiusHtml: string;
  analyticHtml: string;
  generalHtml: string;
  parametricHtml: string;
  perimeterHtml: string;
  areaHtml: string;
}

export interface TriangleDto {
  vertices: Record<string, string>;
  sides: { key: string; name: string; lengthHtml: string }[];
  longest: string[];
  shortest: string[];
  perimeterHtml: string;
  semiperimeterHtml: string;
  areaHtml: string;
  kind: TriangleData["kind"];
  angles: { vertex: string; cosHtml: string; angleHtml: string; degreesHtml: string | null }[];
  centers: Record<string, string>;
  radii: { rHtml: string; RHtml: string };
  euler: Record<LineForm, string | null> | null;
  circles: { incircle: TriangleCircleDto; circumcircle: TriangleCircleDto; ninepoint: TriangleCircleDto };
  excircles: { vertex: string; centerHtml: string; radiusHtml: string }[];
  lines: TriangleLineDto[];
  /** Plain numbers for the drawing only. */
  figure: TriangleData["figure"];
}

export interface TriangleResponseDto {
  ok: boolean;
  data?: TriangleDto;
  code?: string;
  message?: string;
}
