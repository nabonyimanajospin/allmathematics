/**
 * More of the grapher: exact measurements of circles and polygons, slope fields of first-order differential equations with a
 * solution curve (Runge-Kutta), and parametric surfaces in space. Pure code, like graph.ts.
 */

import { PlotExpressionError, compileExpr } from "./plot";
import type { Pt, Pt3, Params } from "./graph";

// --- exact numbers --------------------------------------------------------------------------------------------------------------------
type Frac = [number, number];

const gcd = (a: number, b: number): number => (b === 0 ? Math.abs(a) : gcd(b, a % b));

function frac(n: number, d: number): Frac {
  const g = gcd(n, d) || 1;
  const s = d < 0 ? -1 : 1;
  return [(s * n) / g, (s * d) / g];
}

/** A decimal such as 2.5 as an exact fraction, or null when it has more than 3 decimals. */
function toFrac(v: number): Frac | null {
  const scaled = Math.round(v * 1000);
  if (!Number.isSafeInteger(scaled) || Math.abs(scaled / 1000 - v) > 1e-9) return null;
  return frac(scaled, 1000);
}

const add = (a: Frac, b: Frac): Frac => frac(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
const sub = (a: Frac, b: Frac): Frac => frac(a[0] * b[1] - b[0] * a[1], a[1] * b[1]);
const mul = (a: Frac, b: Frac): Frac => frac(a[0] * b[0], a[1] * b[1]);
const fmtFrac = (f: Frac): string => (f[1] === 1 ? String(f[0]) : `${f[0]}/${f[1]}`);

/** sqrt(n/d) = (k/d') * sqrt(m) with m square-free: returns the coefficient and the radicand. */
function sqrtParts(f: Frac): { coef: Frac; radicand: number } {
  const [n, d] = f;
  let k = 1;
  let m = n * d; // sqrt(n/d) = sqrt(n*d)/d
  for (let p = 2; p * p <= m; p++) {
    while (m % (p * p) === 0) {
      m /= p * p;
      k *= p;
    }
  }
  return { coef: frac(k, d), radicand: m };
}

/** A sum of terms c*sqrt(m), written with like radicals gathered: "3 + 2√2 + √5/2". */
function radicalSum(parts: { coef: Frac; radicand: number }[]): string {
  const byRadicand = new Map<number, Frac>();
  for (const p of parts) byRadicand.set(p.radicand, add(byRadicand.get(p.radicand) ?? [0, 1], p.coef));
  const terms: string[] = [];
  const keys = [...byRadicand.keys()].sort((a, b) => a - b);
  for (const m of keys) {
    const c = byRadicand.get(m)!;
    if (c[0] === 0) continue;
    if (m === 1) terms.push(fmtFrac(c));
    else if (c[0] === c[1]) terms.push(`√${m}`);
    else if (c[1] === 1) terms.push(`${c[0]}√${m}`);
    else terms.push(`${c[0]}√${m}/${c[1]}`);
  }
  return terms.length === 0 ? "0" : terms.join(" + ").replaceAll("+ -", "- ");
}

const fmtNum = (v: number): string => String(parseFloat(v.toPrecision(6)));

export interface ShapeMeasure {
  lines: { label: "radius" | "circumference" | "area" | "perimeter" | "equation"; value: string }[];
  exact: boolean;
}

/** Radius, circumference, area and equation of the circle with centre c through p. */
export function measureCircle(c: Pt, p: Pt): ShapeMeasure {
  const fa = toFrac(c[0]);
  const fb = toFrac(c[1]);
  const fx = toFrac(p[0]);
  const fy = toFrac(p[1]);
  if (fa && fb && fx && fy) {
    const dx = sub(fx, fa);
    const dy = sub(fy, fb);
    const r2 = add(mul(dx, dx), mul(dy, dy));
    const { coef, radicand } = sqrtParts(r2);
    const radius = radicalSum([{ coef, radicand }]);
    const twice = radicalSum([{ coef: mul(coef, [2, 1]), radicand }]);
    const shift = (v: Frac, name: string) => (v[0] === 0 ? name : v[0] < 0 ? `(${name} + ${fmtFrac([-v[0], v[1]])})` : `(${name} - ${fmtFrac(v)})`);
    return {
      exact: true,
      lines: [
        { label: "radius", value: radius },
        { label: "circumference", value: /[+/-]/.test(twice) ? `(${twice})π` : `${twice}π` },
        { label: "area", value: /\//.test(fmtFrac(r2)) ? `(${fmtFrac(r2)})π` : `${fmtFrac(r2)}π` },
        { label: "equation", value: `${shift(fa, "x")}² + ${shift(fb, "y")}² = ${fmtFrac(r2)}` },
      ],
    };
  }
  const r = Math.hypot(p[0] - c[0], p[1] - c[1]);
  return {
    exact: false,
    lines: [
      { label: "radius", value: fmtNum(r) },
      { label: "circumference", value: fmtNum(2 * Math.PI * r) },
      { label: "area", value: fmtNum(Math.PI * r * r) },
      { label: "equation", value: `(x - ${fmtNum(c[0])})² + (y - ${fmtNum(c[1])})² = ${fmtNum(r * r)}` },
    ],
  };
}

/** Perimeter and area (shoelace formula) of the polygon with these vertices in order. */
export function measurePolygon(pts: Pt[]): ShapeMeasure {
  const fr = pts.map((p) => [toFrac(p[0]), toFrac(p[1])] as const);
  if (fr.every(([a, b]) => a && b)) {
    const v = fr.map(([a, b]) => [a!, b!] as [Frac, Frac]);
    let twiceArea: Frac = [0, 1];
    const sides: { coef: Frac; radicand: number }[] = [];
    for (let i = 0; i < v.length; i++) {
      const [x1, y1] = v[i]!;
      const [x2, y2] = v[(i + 1) % v.length]!;
      twiceArea = add(twiceArea, sub(mul(x1, y2), mul(x2, y1)));
      const dx = sub(x2, x1);
      const dy = sub(y2, y1);
      sides.push(sqrtParts(add(mul(dx, dx), mul(dy, dy))));
    }
    const area = mul(twiceArea[0] < 0 ? [-twiceArea[0], twiceArea[1]] : twiceArea, [1, 2]);
    return { exact: true, lines: [{ label: "perimeter", value: radicalSum(sides) }, { label: "area", value: fmtFrac(area) }] };
  }
  let twice = 0;
  let per = 0;
  for (let i = 0; i < pts.length; i++) {
    const [x1, y1] = pts[i]!;
    const [x2, y2] = pts[(i + 1) % pts.length]!;
    twice += x1 * y2 - x2 * y1;
    per += Math.hypot(x2 - x1, y2 - y1);
  }
  return { exact: false, lines: [{ label: "perimeter", value: fmtNum(per) }, { label: "area", value: fmtNum(Math.abs(twice) / 2) }] };
}

/** A circle as a closed polyline. */
export function circlePoints(c: Pt, p: Pt, n = 240): Pt[] {
  const r = Math.hypot(p[0] - c[0], p[1] - c[1]);
  return Array.from({ length: n + 1 }, (_, i) => [c[0] + r * Math.cos((2 * Math.PI * i) / n), c[1] + r * Math.sin((2 * Math.PI * i) / n)] as Pt);
}

// --- first-order differential equations y' = f(x, y) ----------------------------------------------------------------------------------
/** The function f(x, y) of y' = f(x, y); throws PlotExpressionError when the expression cannot be read. */
export function slopeFunction(expr: string, params: Params): (x: number, y: number) => number {
  const names = Object.keys(params);
  const f = compileExpr(expr, ["x", "y", ...names]);
  const values = names.map((n) => params[n]!);
  return (x, y) => f(x, y, ...values);
}

/** The solution through (x0, y0) by the classical Runge-Kutta method, forward and backward, as pieces inside the view. */
export function solutionCurve(f: (x: number, y: number) => number, x0: number, y0: number, xmin: number, xmax: number, ylimit: number, steps = 600): Pt[][] {
  const h = (xmax - xmin) / steps;
  const go = (dir: 1 | -1): Pt[] => {
    const out: Pt[] = [];
    let x = x0;
    let y = y0;
    const step = dir * h;
    for (let i = 0; i < steps * 2; i++) {
      const k1 = f(x, y);
      const k2 = f(x + step / 2, y + (step / 2) * k1);
      const k3 = f(x + step / 2, y + (step / 2) * k2);
      const k4 = f(x + step, y + step * k3);
      const yn = y + (step / 6) * (k1 + 2 * k2 + 2 * k3 + k4);
      x += step;
      if (!Number.isFinite(yn) || Math.abs(yn) > ylimit || x < xmin - h || x > xmax + h) break;
      y = yn;
      out.push([x, y]);
    }
    return out;
  };
  const back = go(-1).reverse();
  const fwd = go(1);
  return [[...back, [x0, y0] as Pt, ...fwd]];
}

// --- parametric surfaces -------------------------------------------------------------------------------------------------------------
export interface ParamSurface {
  x: string;
  y: string;
  z: string;
  u: [string, string];
  v: [string, string];
}

/**
 * Reads  (x(u,v), y(u,v), z(u,v)), u in [a, b], v in [c, d]  or returns null when the text is not of this form
 * (the ranges default to u in [0, 2*pi] and v in [0, 2*pi]).
 */
export function parseParamSurface(text: string): ParamSurface | null {
  const m = /^\(\s*(.+)\s*\)\s*(?:,\s*u\s*in\s*\[\s*(.+?)\s*,\s*(.+?)\s*\]\s*,\s*v\s*in\s*\[\s*(.+?)\s*,\s*(.+?)\s*\])?$/.exec(text.trim());
  if (!m) return null;
  let depth = 0;
  const parts: string[] = [];
  let start = 0;
  const body = m[1]!;
  for (let i = 0; i < body.length; i++) {
    const c = body[i];
    if (c === "(" || c === "[") depth++;
    else if (c === ")" || c === "]") depth--;
    else if (c === "," && depth === 0) {
      parts.push(body.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(body.slice(start));
  if (parts.length !== 3) return null;
  if (!/\bu\b|\bv\b/.test(body)) return null;
  return { x: parts[0]!.trim(), y: parts[1]!.trim(), z: parts[2]!.trim(), u: [m[2] ?? "0", m[3] ?? "2*pi"], v: [m[4] ?? "0", m[5] ?? "2*pi"] };
}

/** A grid of points of a parametric surface; a point where a coordinate is not defined is null. `read` turns a text into a number (it may use the sliders). */
export function sampleParamSurface(s: ParamSurface, params: Params, read: (text: string) => number, n = 36): (Pt3 | null)[][] {
  const names = Object.keys(params);
  const vals = names.map((k) => params[k]!);
  const fx = compileExpr(s.x, ["u", "v", ...names]);
  const fy = compileExpr(s.y, ["u", "v", ...names]);
  const fz = compileExpr(s.z, ["u", "v", ...names]);
  const [u0, u1, v0, v1] = [read(s.u[0]), read(s.u[1]), read(s.v[0]), read(s.v[1])];
  if (![u0, u1, v0, v1].every(Number.isFinite)) throw new PlotExpressionError("The ranges of u and v must be numbers");
  const grid: (Pt3 | null)[][] = [];
  for (let i = 0; i <= n; i++) {
    const row: (Pt3 | null)[] = [];
    const u = u0 + ((u1 - u0) * i) / n;
    for (let j = 0; j <= n; j++) {
      const v = v0 + ((v1 - v0) * j) / n;
      const p: Pt3 = [fx(u, v, ...vals), fy(u, v, ...vals), fz(u, v, ...vals)];
      row.push(p.every(Number.isFinite) && p.every((c) => Math.abs(c) < 1e6) ? p : null);
    }
    grid.push(row);
  }
  return grid;
}
