/**
 * Recognizes a triangle problem typed in the solver's text box, so that the solver can offer the triangle toolkit:
 * "triangle A(1,2), B(3,4), C(5,0)", "area of the triangle with vertices (0,0), (4,0), (0,3)" or simply "A(1,2) B(3,4) C(5,6)".
 */

const NUMBER = String.raw`[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:/\d+)?`;
const PAIR = new RegExp(String.raw`\(\s*(${NUMBER})\s*[,;]\s*(${NUMBER})\s*\)`, "g");

/** The first three points written as (x, y), when the text speaks of a triangle or labels three points A, B and C; otherwise null. */
export function findTriangleVertices(text: string): string[][] | null {
  const points = [...text.matchAll(PAIR)].map((m) => [m[1]!, m[2]!]);
  if (points.length < 3) return null;
  const speaksOfATriangle = /triang/i.test(text);
  const labelsABC = ["A", "B", "C"].every((l) => new RegExp(String.raw`\b${l}\s*=?\s*\(`).test(text));
  if (!speaksOfATriangle && !(labelsABC && points.length === 3)) return null;
  return points.slice(0, 3);
}
