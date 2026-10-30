/**
 * The mathematics of the grapher: reading what the learner typed (implicit multiplication, y=f(x), x=g(y), r=f(theta), implicit curves,
 * parametric curves, points, surfaces) and sampling it. Pure code with the safe expression evaluator of plot.ts: no eval, no Function.
 */

import { circlePoints, slopeFunction, solutionCurve } from "./graph-geometry";
import { PlotExpressionError, compileExpr } from "./plot";

export type Pt = [number, number];

const FUNCTION_NAMES = new Set(["sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "sqrt", "exp", "ln", "abs", "log", "floor", "ceil", "round", "sign", "cbrt", "sec", "csc", "cot", "logten", "logtwo"]);
const CONSTANT_NAMES = new Set(["pi", "e"]);
/** Letters that can be a slider (a parameter): not the variables, not the constants. */
const PARAM_LETTERS = new Set("abcdfghjklmnpqsuvwz".split(""));

/** Letters that may be multiplied without a sign when written together. */
const PRODUCT_LETTERS = new Set([..."xyzt", ...PARAM_LETTERS, "e"]);

const SUPERSCRIPTS: Record<string, string> = { "²": "^2", "³": "^3", "⁴": "^4", "⁻¹": "^(-1)" };

/** Rewrites what a learner types into the form the evaluator reads: `2x` -> `2*x`, `x(x+1)` -> `x*(x+1)`, `sin x` -> `sin(x)`, `xy` -> `x*y`. */
export function normalizeExpr(src: string): string {
  let s = src.trim().replaceAll("−", "-").replaceAll("×", "*").replaceAll("·", "*").replaceAll("π", "pi").replaceAll("√", "sqrt");
  for (const [k, v] of Object.entries(SUPERSCRIPTS)) s = s.replaceAll(k, v);
  // (a number may stand right before it: 2log10(x))
  s = s.replace(/log10(?![A-Za-z0-9_])/g, "logten").replace(/log2(?![A-Za-z0-9_])/g, "logtwo").replace(/\blog\(/g, "ln(");
  const tokens = s.match(/\d+(?:\.\d+)?|[A-Za-z_]+|[-+*/^(),]|\s+/g) ?? [];
  const out: string[] = [];
  const items = tokens.filter((t) => !/^\s+$/.test(t));
  // split runs of letters that are not a known word into single letters
  const flat: string[] = [];
  for (const t of items) {
    // a run of variable letters is a product (xy, ax); any other word is kept whole so that the error names it (foo, sinx)
    if (/^[A-Za-z]+$/.test(t) && !FUNCTION_NAMES.has(t) && !CONSTANT_NAMES.has(t) && t !== "theta" && t.length > 1 && [...t].every((ch) => PRODUCT_LETTERS.has(ch))) {
      for (const ch of t) flat.push(ch);
    } else flat.push(t);
  }
  const isFn = (t: string) => FUNCTION_NAMES.has(t);
  const isAtomEnd = (t: string) => /^(\d|[A-Za-z_])/.test(t) && !isFn(t) || t === ")";
  const isAtomStart = (t: string) => /^(\d|[A-Za-z_])/.test(t) || t === "(";
  for (let i = 0; i < flat.length; i++) {
    const t = flat[i]!;
    const prev = flat[i - 1];
    // a word of several letters that is not a constant, directly followed by "(", is a function call (the evaluator names it if it is unknown)
    const wordCall = t === "(" && prev !== undefined && /^[A-Za-z]{2,}$/.test(prev) && !CONSTANT_NAMES.has(prev) && prev !== "theta";
    if (prev !== undefined && isAtomEnd(prev) && isAtomStart(t) && !wordCall) out.push("*");
    out.push(t);
    // a function without parentheses takes the next atom: sin x -> sin(x)
    if (isFn(t) && flat[i + 1] !== undefined && flat[i + 1] !== "(") {
      const nxt = flat[i + 1]!;
      if (/^(\d|[A-Za-z_])/.test(nxt)) {
        out.push("(", nxt, ")");
        i += 1;
      }
    }
  }
  return out.join("");
}

export type GraphItem =
  | { kind: "function"; expr: string }
  | { kind: "xfunction"; expr: string }
  | { kind: "implicit"; lhs: string; rhs: string }
  | { kind: "parametric"; x: string; y: string; t0: string; t1: string }
  | { kind: "polar"; expr: string }
  | { kind: "point"; x: string; y: string; name?: string }
  | { kind: "segment"; a: string; b: string; mode: "segment" | "line" }
  | { kind: "circle"; center: string; through: string }
  | { kind: "polygon"; names: string[] }
  /** y' = f(x, y): the slope field, and the solution through the named point when there is one. */
  | { kind: "slopefield"; expr: string; at?: string }
  | { kind: "region"; lhs: string; rhs: string; op: "<" | ">" | "<=" | ">=" }
  | { kind: "empty" }
  | { kind: "error"; message: string };

function splitTopLevel(s: string, sep: string): string[] {
  const parts: string[] = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === "(" || c === "[") depth++;
    else if (c === ")" || c === "]") depth--;
    else if (c === sep && depth === 0) {
      parts.push(s.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(s.slice(start));
  return parts;
}

const usesName = (expr: string, name: string): boolean => new RegExp(`(^|[^A-Za-z_])${name}([^A-Za-z_]|$)`).test(expr);

/** What kind of object is this line? */
export function classify(text: string): GraphItem {
  const raw = text.trim();
  if (raw === "") return { kind: "empty" };
  try {
    // a segment or a line through two named points:  segment(A, B)   line(A, B)
    const seg = /^(segment|seg|line)\s*\(\s*([A-Z][A-Za-z0-9]*)\s*,\s*([A-Z][A-Za-z0-9]*)\s*\)$/i.exec(raw);
    if (seg) return { kind: "segment", a: seg[2]!, b: seg[3]!, mode: seg[1]!.toLowerCase() === "line" ? "line" : "segment" };
    // a circle with its centre and a point on it, and a polygon through named points:  circle(A, B)   polygon(A, B, C)
    const circ = /^circle\s*\(\s*([A-Z][A-Za-z0-9]*)\s*,\s*([A-Z][A-Za-z0-9]*)\s*\)$/i.exec(raw);
    if (circ) return { kind: "circle", center: circ[1]!, through: circ[2]! };
    const poly = /^polygon\s*\((.+)\)$/i.exec(raw);
    if (poly) {
      const names = poly[1]!.split(",").map((n) => n.trim());
      if (names.length < 3 || names.length > 12 || names.some((n) => !/^[A-Z][A-Za-z0-9]*$/.test(n))) return { kind: "error", message: "Write the polygon with at least three named points, for example polygon(A, B, C)." };
      return { kind: "polygon", names };
    }
    // a first-order differential equation:  y' = x - y   or   ode(y' = x - y, A)  for the solution through the point A
    const ode = /^ode\s*\(\s*(?:y'|dy\s*\/\s*dx)\s*=\s*(.+?)\s*,\s*([A-Z][A-Za-z0-9]*)\s*\)$/i.exec(raw);
    if (ode) return { kind: "slopefield", expr: normalizeExpr(ode[1]!), at: ode[2]! };
    const field = /^(?:y'|dy\s*\/\s*dx)\s*=\s*(.+)$/i.exec(raw);
    if (field) return { kind: "slopefield", expr: normalizeExpr(field[1]!) };
    // a named point:  P(2, 3)   A = (1, 2)   (a capital letter, so that f(x) and sin(x) are still functions)
    const named = /^([A-Z][A-Za-z0-9]*)\s*=?\s*\((.*)\)$/.exec(raw);
    if (named) {
      const coords = splitTopLevel(named[2]!, ",");
      if (coords.length === 2) {
        const [px, py] = coords.map((p) => normalizeExpr(p)) as [string, string];
        return { kind: "point", x: px, y: py, name: named[1]! };
      }
      return { kind: "error", message: `Write the point as ${named[1]!}(x, y), for example ${named[1]!}(2, 3).` };
    }
    // a point needs a capital letter (a small letter is a slider or a variable)
    const small = /^[a-z][A-Za-z0-9]*\s*=\s*\((.*)\)$/.exec(raw);
    if (small && splitTopLevel(small[1]!, ",").length === 2) return { kind: "error", message: "Name a point with a capital letter, for example A = (1, 2)." };
    // (x(t), y(t)) with an optional range:  (cos(t), sin(t)), t in [0, 2pi]
    const m = /^\((.*)\)\s*(?:,\s*(?:for\s+)?t\s*(?:in|=)\s*\[?\s*(.+?)\s*(?:,|\.\.|to)\s*(.+?)\s*\]?)?$/.exec(raw);
    if (m && splitTopLevel(m[1]!, ",").length === 2) {
      const [px, py] = splitTopLevel(m[1]!, ",").map((p) => normalizeExpr(p)) as [string, string];
      if (usesName(px, "t") || usesName(py, "t")) {
        const t0 = m[2] !== undefined ? normalizeExpr(m[2]) : "0";
        const t1 = m[3] !== undefined ? normalizeExpr(m[3]) : "2*pi";
        compileExpr(px, ["t"]);
        compileExpr(py, ["t"]);
        return { kind: "parametric", x: px, y: py, t0, t1 };
      }
      return { kind: "point", x: px, y: py };
    }
    // an inequality:  y > x^2,  x^2 + y^2 <= 4
    const ineq = /^(.+?)(<=|>=|≤|≥|<|>)(.+)$/.exec(raw);
    if (ineq && !ineq[3]!.includes("=") && !/[<>]/.test(ineq[3]!)) {
      const op = ({ "≤": "<=", "≥": ">=" } as Record<string, string>)[ineq[2]!] ?? ineq[2]!;
      const lhs = normalizeExpr(ineq[1]!);
      const rhs = normalizeExpr(ineq[3]!);
      if (!usesName(lhs + " " + rhs, "x") && !usesName(lhs + " " + rhs, "y")) return { kind: "error", message: "An inequality needs x or y." };
      return { kind: "region", lhs, rhs, op: op as "<" | ">" | "<=" | ">=" };
    }
    if (/[<>≤≥]/.test(raw)) return { kind: "error", message: "Use one inequality sign, for example y > x^2." };
    const sides = splitTopLevel(raw, "=");
    if (sides.length > 2) return { kind: "error", message: "Use only one = sign." };
    if (sides.length === 2) {
      const left = sides[0]!.trim();
      const right = sides[1]!.trim();
      // y = x^2*y is a relation between x and y (an implicit curve), not a function of x
      if (/^y$/i.test(left) && usesName(right, "y")) return { kind: "implicit", lhs: "y", rhs: normalizeExpr(right) };
      if (/^(y|f\(x\))$/i.test(left)) return { kind: "function", expr: normalizeExpr(right) };
      if (/^x$/i.test(left) && !usesName(right, "x")) return { kind: "xfunction", expr: normalizeExpr(right) };
      if (/^r$/i.test(left)) return { kind: "polar", expr: normalizeExpr(right).replaceAll("theta", "t") };
      const lhs = normalizeExpr(left);
      const rhs = normalizeExpr(right);
      if (!usesName(lhs + " " + rhs, "x") && !usesName(lhs + " " + rhs, "y")) return { kind: "error", message: "An equation needs x or y." };
      return { kind: "implicit", lhs, rhs };
    }
    return { kind: "function", expr: normalizeExpr(raw) };
  } catch (e) {
    return { kind: "error", message: e instanceof PlotExpressionError ? e.message : "I could not read this." };
  }
}

/** The names of the sliders needed by the items (single letters that are not x, y, t, r or a constant). */
export function parameterNames(items: GraphItem[]): string[] {
  const texts: string[] = [];
  for (const it of items) {
    if (it.kind === "function" || it.kind === "xfunction" || it.kind === "polar") texts.push(it.expr);
    else if (it.kind === "implicit" || it.kind === "region") texts.push(it.lhs, it.rhs);
    else if (it.kind === "parametric") texts.push(it.x, it.y, it.t0, it.t1);
    else if (it.kind === "point") texts.push(it.x, it.y);
    else if (it.kind === "slopefield") texts.push(it.expr);
  }
  const found = new Set<string>();
  for (const t of texts) for (const m of t.matchAll(/(^|[^A-Za-z_])([a-z])(?![A-Za-z_(])/g)) if (PARAM_LETTERS.has(m[2]!)) found.add(m[2]!);
  return [...found].sort();
}

export type Params = Record<string, number>;

function bind(expr: string, vars: string[], params: Params): (...a: number[]) => number {
  const names = Object.keys(params);
  const f = compileExpr(expr, [...vars, ...names]);
  const values = names.map((n) => params[n]!);
  return (...a: number[]) => f(...a, ...values);
}

/** The value of a constant expression such as `2*pi` (it may use the sliders). Throws PlotExpressionError when it is not a number. */
export function evalConstant(text: string, params: Params = {}): number {
  const v = bind(normalizeExpr(text), [], params)();
  if (!Number.isFinite(v)) throw new PlotExpressionError(`“${text}” is not a number`);
  return v;
}

// --- sampling a function of one variable ---------------------------------------------------------------------------
export interface View {
  xmin: number;
  xmax: number;
  ymin: number;
  ymax: number;
}

/** Pieces of the curve y=f(x): a piece ends where the function is undefined, leaves the picture or jumps over an asymptote. */
export function sampleFunction(f: (x: number) => number, view: View, samples = 800): Pt[][] {
  const pieces: Pt[][] = [];
  let cur: Pt[] = [];
  const span = view.ymax - view.ymin;
  let prev: Pt | null = null;
  for (let i = 0; i <= samples; i++) {
    const x = view.xmin + ((view.xmax - view.xmin) * i) / samples;
    const y = f(x);
    const ok = Number.isFinite(y) && Math.abs(y) < 1e7;
    if (!ok) {
      if (cur.length > 1) pieces.push(cur);
      cur = [];
      prev = null;
      continue;
    }
    if (prev && Math.abs(y - prev[1]) > 4 * span && Math.sign(y) !== Math.sign(prev[1])) {
      if (cur.length > 1) pieces.push(cur);
      cur = [];
    }
    cur.push([x, y]);
    prev = [x, y];
  }
  if (cur.length > 1) pieces.push(cur);
  return pieces;
}

export function sampleParametric(fx: (t: number) => number, fy: (t: number) => number, t0: number, t1: number, samples = 1200): Pt[][] {
  const pieces: Pt[][] = [];
  let cur: Pt[] = [];
  for (let i = 0; i <= samples; i++) {
    const t = t0 + ((t1 - t0) * i) / samples;
    const x = fx(t);
    const y = fy(t);
    if (!Number.isFinite(x) || !Number.isFinite(y)) {
      if (cur.length > 1) pieces.push(cur);
      cur = [];
    } else cur.push([x, y]);
  }
  if (cur.length > 1) pieces.push(cur);
  return pieces;
}

/** The segments of the curve F(x, y) = 0 inside the view (marching squares with linear interpolation). */
export function marchingSquares(F: (x: number, y: number) => number, view: View, nx = 160, ny = 120): [number, number, number, number][] {
  const dx = (view.xmax - view.xmin) / nx;
  const dy = (view.ymax - view.ymin) / ny;
  const val: number[][] = [];
  for (let j = 0; j <= ny; j++) {
    const row: number[] = [];
    for (let i = 0; i <= nx; i++) row.push(F(view.xmin + i * dx, view.ymin + j * dy));
    val.push(row);
  }
  const segs: [number, number, number, number][] = [];
  const lerp = (a: number, b: number, va: number, vb: number): number => (va === vb ? a : a + ((b - a) * (0 - va)) / (vb - va));
  for (let j = 0; j < ny; j++) {
    for (let i = 0; i < nx; i++) {
      const v0 = val[j]![i]!;
      const v1 = val[j]![i + 1]!;
      const v2 = val[j + 1]![i + 1]!;
      const v3 = val[j + 1]![i]!;
      if (![v0, v1, v2, v3].every(Number.isFinite)) continue;
      const x0 = view.xmin + i * dx;
      const y0 = view.ymin + j * dy;
      const idx = (v0 > 0 ? 1 : 0) | (v1 > 0 ? 2 : 0) | (v2 > 0 ? 4 : 0) | (v3 > 0 ? 8 : 0);
      if (idx === 0 || idx === 15) continue;
      const bottom: Pt = [lerp(x0, x0 + dx, v0, v1), y0];
      const right: Pt = [x0 + dx, lerp(y0, y0 + dy, v1, v2)];
      const top: Pt = [lerp(x0, x0 + dx, v3, v2), y0 + dy];
      const left: Pt = [x0, lerp(y0, y0 + dy, v0, v3)];
      const push = (a: Pt, b: Pt) => segs.push([a[0], a[1], b[0], b[1]]);
      switch (idx) {
        case 1: case 14: push(left, bottom); break;
        case 2: case 13: push(bottom, right); break;
        case 3: case 12: push(left, right); break;
        case 4: case 11: push(right, top); break;
        case 6: case 9: push(bottom, top); break;
        case 7: case 8: push(left, top); break;
        case 5: push(left, top); push(bottom, right); break;
        case 10: push(left, bottom); push(right, top); break;
      }
    }
  }
  return segs;
}

/** What is needed to draw one item in the current view. */
export type Drawable =
  | { kind: "lines"; pieces: Pt[][] }
  | { kind: "segments"; segments: [number, number, number, number][] }
  | { kind: "point"; at: Pt }
  | { kind: "polygon"; pts: Pt[] }
  | { kind: "slopefield"; f: (x: number, y: number) => number; curve: Pt[][] }
  | { kind: "region"; inside: (x: number, y: number) => boolean; boundary: [number, number, number, number][]; strict: boolean }
  | { kind: "error"; message: string }
  | { kind: "none" };

/** The named points (A(1, 2), P = (3, 4)) of the items, by name. */
export function namedPoints(items: GraphItem[], params: Params): Record<string, Pt> {
  const out: Record<string, Pt> = {};
  for (const it of items) {
    if (it.kind !== "point" || !it.name) continue;
    try {
      const x = bind(it.x, [], params)();
      const y = bind(it.y, [], params)();
      if (Number.isFinite(x) && Number.isFinite(y)) out[it.name] = [x, y];
    } catch {
      /* a point that cannot be read is simply not available to segments */
    }
  }
  return out;
}

const SAME_PLACE = 1e-9;
const samePlace = (p: Pt, q: Pt): boolean => Math.abs(p[0] - q[0]) < SAME_PLACE && Math.abs(p[1] - q[1]) < SAME_PLACE;
const shown = (v: number): string => String(parseFloat(v.toPrecision(6)));

/** The position of every point item (named or not) that can be evaluated, with its row. */
export function pointPositions(items: GraphItem[], params: Params): { index: number; name?: string; at: Pt }[] {
  const out: { index: number; name?: string; at: Pt }[] = [];
  items.forEach((it, index) => {
    if (it.kind !== "point") return;
    try {
      const at: Pt = [bind(it.x, [], params)(), bind(it.y, [], params)()];
      if (Number.isFinite(at[0]) && Number.isFinite(at[1])) out.push({ index, ...(it.name ? { name: it.name } : {}), at });
    } catch {
      /* a point that cannot be read has no position */
    }
  });
  return out;
}

/** The point that is at `at` (the same place), if any; `except` is a row to leave out (the point that is being moved). */
export function pointAtPlace(items: GraphItem[], params: Params, at: Pt, except?: number): { index: number; name?: string; at: Pt } | undefined {
  return pointPositions(items, params).find((p) => p.index !== except && samePlace(p.at, at));
}

/**
 * Two points cannot have the same name, and two points cannot be in the same place: the later row of such a pair becomes an error that
 * says why, so it is not drawn and segments cannot use it. A point that depends on a slider (P(a, 2)) is not compared by place, because
 * it moves with the slider; its name is still checked.
 */
export function rejectDuplicatePoints(items: GraphItem[], params: Params): GraphItem[] {
  const positions = new Map(pointPositions(items, params).map((p) => [p.index, p.at]));
  const names = new Set<string>();
  const accepted: { name?: string; at: Pt }[] = [];
  return items.map((it, index) => {
    if (it.kind !== "point") return it;
    if (it.name && names.has(it.name)) return { kind: "error", message: `The name ${it.name} is already used by another point. Choose another letter.` };
    const at = positions.get(index);
    const fixed = parameterNames([it]).length === 0;
    if (at && fixed) {
      const twin = accepted.find((p) => samePlace(p.at, at));
      if (twin) {
        const where = `(${shown(at[0])}, ${shown(at[1])})`;
        return { kind: "error", message: `${twin.name ? `The point ${twin.name} is` : "A point is"} already at ${where}. Two points cannot be in the same place.` };
      }
    }
    if (it.name) names.add(it.name);
    if (at && fixed) accepted.push({ ...(it.name ? { name: it.name } : {}), at });
    return it;
  });
}

export function drawable(item: GraphItem, params: Params, view: View, points: Record<string, Pt> = {}): Drawable {
  try {
    switch (item.kind) {
      case "empty":
        return { kind: "none" };
      case "circle": {
        const c = points[item.center];
        const p = points[item.through];
        if (!c) return { kind: "error", message: `The point ${item.center} is not defined. Add it, for example ${item.center}(0, 0).` };
        if (!p) return { kind: "error", message: `The point ${item.through} is not defined. Add it, for example ${item.through}(3, 0).` };
        if (c[0] === p[0] && c[1] === p[1]) return { kind: "error", message: `${item.center} and ${item.through} are the same point: the circle has radius 0.` };
        return { kind: "lines", pieces: [circlePoints(c, p)] };
      }
      case "polygon": {
        const pts: Pt[] = [];
        for (const n of item.names) {
          const p = points[n];
          if (!p) return { kind: "error", message: `The point ${n} is not defined. Add it, for example ${n}(1, 2).` };
          pts.push(p);
        }
        return { kind: "polygon", pts };
      }
      case "slopefield": {
        const f = slopeFunction(item.expr, params);
        let curve: Pt[][] = [];
        if (item.at !== undefined) {
          const p = points[item.at];
          if (!p) return { kind: "error", message: `The point ${item.at} is not defined. Add it, for example ${item.at}(0, 1).` };
          curve = solutionCurve(f, p[0], p[1], view.xmin, view.xmax, 50 * (view.ymax - view.ymin));
        }
        return { kind: "slopefield", f, curve };
      }
      case "segment": {
        const a = points[item.a];
        const b = points[item.b];
        if (!a) return { kind: "error", message: `The point ${item.a} is not defined. Add it, for example ${item.a}(1, 2).` };
        if (!b) return { kind: "error", message: `The point ${item.b} is not defined. Add it, for example ${item.b}(3, 4).` };
        if (a[0] === b[0] && a[1] === b[1]) return { kind: "error", message: `${item.a} and ${item.b} are the same point.` };
        if (item.mode === "segment") return { kind: "lines", pieces: [[a, b]] };
        // a line: extend far beyond the picture in both directions
        const reach = 1e4;
        const dx = b[0] - a[0];
        const dy = b[1] - a[1];
        return { kind: "lines", pieces: [[[a[0] - reach * dx, a[1] - reach * dy], [a[0] + reach * dx, a[1] + reach * dy]]] };
      }
      case "error":
        return { kind: "error", message: item.message };
      case "function": {
        const f = bind(item.expr, ["x"], params);
        return { kind: "lines", pieces: sampleFunction(f, view) };
      }
      case "xfunction": {
        const g = bind(item.expr, ["y"], params);
        const flip = sampleFunction(g, { xmin: view.ymin, xmax: view.ymax, ymin: view.xmin, ymax: view.xmax });
        return { kind: "lines", pieces: flip.map((p) => p.map(([a, b]) => [b, a] as Pt)) };
      }
      case "implicit": {
        const l = bind(item.lhs, ["x", "y"], params);
        const r = bind(item.rhs, ["x", "y"], params);
        return { kind: "segments", segments: marchingSquares((x, y) => l(x, y) - r(x, y), view) };
      }
      case "region": {
        const l = bind(item.lhs, ["x", "y"], params);
        const r = bind(item.rhs, ["x", "y"], params);
        const strict = item.op === "<" || item.op === ">";
        const less = item.op === "<" || item.op === "<=";
        const inside = (x: number, y: number): boolean => {
          const d = l(x, y) - r(x, y);
          return Number.isFinite(d) && (less ? (strict ? d < 0 : d <= 0) : strict ? d > 0 : d >= 0);
        };
        return { kind: "region", inside, strict, boundary: marchingSquares((x, y) => l(x, y) - r(x, y), view) };
      }
      case "polar": {
        const r = bind(item.expr, ["t"], params);
        return { kind: "lines", pieces: sampleParametric((t) => r(t) * Math.cos(t), (t) => r(t) * Math.sin(t), 0, 12 * Math.PI, 2400) };
      }
      case "parametric": {
        const fx = bind(item.x, ["t"], params);
        const fy = bind(item.y, ["t"], params);
        const t0 = bind(item.t0, [], params)();
        const t1 = bind(item.t1, [], params)();
        if (!Number.isFinite(t0) || !Number.isFinite(t1)) return { kind: "error", message: "The range of t is not a number." };
        return { kind: "lines", pieces: sampleParametric(fx, fy, t0, t1) };
      }
      case "point": {
        const x = bind(item.x, [], params)();
        const y = bind(item.y, [], params)();
        return Number.isFinite(x) && Number.isFinite(y) ? { kind: "point", at: [x, y] } : { kind: "error", message: "The point is not defined." };
      }
    }
  } catch (e) {
    return { kind: "error", message: e instanceof PlotExpressionError ? e.message : "I could not draw this." };
  }
}

// --- surfaces in space ---------------------------------------------------------------------------------------------
export type Pt3 = [number, number, number];

/** A grid of points (x, y, f(x, y)) for z = f(x, y); a point where f is not defined is null. */
export function sampleSurface(expr: string, params: Params, xr: [number, number], yr: [number, number], n = 40): (Pt3 | null)[][] {
  const f = bind(normalizeExpr(expr), ["x", "y"], params);
  const grid: (Pt3 | null)[][] = [];
  for (let j = 0; j <= n; j++) {
    const row: (Pt3 | null)[] = [];
    for (let i = 0; i <= n; i++) {
      const x = xr[0] + ((xr[1] - xr[0]) * i) / n;
      const y = yr[0] + ((yr[1] - yr[0]) * j) / n;
      const z = f(x, y);
      row.push(Number.isFinite(z) && Math.abs(z) < 1e6 ? [x, y, z] : null);
    }
    grid.push(row);
  }
  return grid;
}

/** A parametric curve (x(t), y(t), z(t)) in space. */
export function sampleCurve3(ex: string, ey: string, ez: string, params: Params, t0: number, t1: number, n = 600): Pt3[] {
  const fx = bind(normalizeExpr(ex), ["t"], params);
  const fy = bind(normalizeExpr(ey), ["t"], params);
  const fz = bind(normalizeExpr(ez), ["t"], params);
  const out: Pt3[] = [];
  for (let i = 0; i <= n; i++) {
    const t = t0 + ((t1 - t0) * i) / n;
    const p: Pt3 = [fx(t), fy(t), fz(t)];
    if (p.every(Number.isFinite)) out.push(p);
  }
  return out;
}

// --- special points -------------------------------------------------------------------------------------------------
export interface SpecialPoint {
  at: Pt;
  kind: "root" | "intersection";
  /** 1-based numbers of the lines that meet here (one for a root). */
  lines: number[];
}

/** The x in [a, b] where g changes sign, found by bisection (g(a) and g(b) have opposite signs). */
function bisect(g: (x: number) => number, a: number, b: number): number {
  let lo = a;
  let hi = b;
  let glo = g(lo);
  for (let k = 0; k < 60; k++) {
    const mid = (lo + hi) / 2;
    const gm = g(mid);
    if (gm === 0) return mid;
    if (Math.sign(gm) === Math.sign(glo)) {
      lo = mid;
      glo = gm;
    } else hi = mid;
  }
  return (lo + hi) / 2;
}

/** Where g(x) = 0 inside [xmin, xmax]; a jump over an asymptote is not a zero. */
function zeros(g: (x: number) => number, xmin: number, xmax: number, samples = 1600): number[] {
  const out: number[] = [];
  let px = xmin;
  let pv = g(px);
  for (let i = 1; i <= samples; i++) {
    const x = xmin + ((xmax - xmin) * i) / samples;
    const v = g(x);
    if (Number.isFinite(pv) && Number.isFinite(v)) {
      if (pv === 0) out.push(px);
      else if (Math.sign(pv) !== Math.sign(v) && v !== 0) {
        const z = bisect(g, px, x);
        if (Math.abs(g(z)) < 1e-6 * Math.max(1, Math.abs(pv), Math.abs(v))) out.push(z);
      }
    }
    px = x;
    pv = v;
  }
  if (Number.isFinite(pv) && pv === 0) out.push(px);
  return out;
}

/**
 * The roots (where a line y = f(x) meets the x-axis) and the intersections of two such lines, inside the view.
 * These are found numerically from the picture, so they are approximate: the learner reads them as a guide.
 */
export function specialPoints(items: GraphItem[], params: Params, view: View, limit = 24): SpecialPoint[] {
  const fns: { n: number; f: (x: number) => number }[] = [];
  items.forEach((it, i) => {
    if (it.kind !== "function") return;
    try {
      fns.push({ n: i + 1, f: bind(it.expr, ["x"], params) });
    } catch {
      /* an unreadable line has no special points */
    }
  });
  const out: SpecialPoint[] = [];
  const dedupe = (x: number, kind: SpecialPoint["kind"], lines: number[], y: number) => {
    if (!Number.isFinite(y)) return;
    const same = out.find((p) => Math.abs(p.at[0] - x) < 1e-6 && Math.abs(p.at[1] - y) < 1e-6);
    if (!same) {
      out.push({ at: [x, y], kind, lines });
      return;
    }
    for (const l of lines) if (!same.lines.includes(l)) same.lines.push(l);
    if (same.lines.length > 1) same.kind = "intersection";
  };
  for (const { n, f } of fns) for (const x of zeros(f, view.xmin, view.xmax)) dedupe(x, "root", [n], 0);
  for (let i = 0; i < fns.length; i++) {
    for (let j = i + 1; j < fns.length; j++) {
      const a = fns[i]!;
      const b = fns[j]!;
      for (const x of zeros((t) => a.f(t) - b.f(t), view.xmin, view.xmax)) dedupe(x, "intersection", [a.n, b.n], a.f(x));
    }
  }
  return out.slice(0, limit);
}

// --- measurements of segments and lines ------------------------------------------------------------------------------
type Frac = [number, number];

const gcd = (a: number, b: number): number => (b === 0 ? Math.abs(a) : gcd(b, a % b));

function frac(n: number, d: number): Frac {
  const g = gcd(n, d) || 1;
  const s = d < 0 ? -1 : 1;
  return [(s * n) / g, (s * d) / g];
}

/** A decimal such as 2.5 or -0.25 as an exact fraction, or null when it has more than 3 decimals. */
function toFrac(v: number): Frac | null {
  const scaled = Math.round(v * 1000);
  if (!Number.isSafeInteger(scaled) || Math.abs(scaled / 1000 - v) > 1e-9) return null;
  return frac(scaled, 1000);
}

const sub = (a: Frac, b: Frac): Frac => frac(a[0] * b[1] - b[0] * a[1], a[1] * b[1]);
const add = (a: Frac, b: Frac): Frac => frac(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
const mul = (a: Frac, b: Frac): Frac => frac(a[0] * b[0], a[1] * b[1]);
const div = (a: Frac, b: Frac): Frac => frac(a[0] * b[1], a[1] * b[0]);
const fmtFrac = (f: Frac): string => (f[1] === 1 ? String(f[0]) : `${f[0]}/${f[1]}`);

/** sqrt of a non-negative fraction as text: 13 -> "√13", 8 -> "2√2", 9/4 -> "3/2", 2/9 -> "√2/3". */
function sqrtText(f: Frac): string {
  const [n, d] = f;
  const big = n * d; // sqrt(n/d) = sqrt(n*d)/d
  let k = 1;
  let m = big;
  for (let p = 2; p * p <= m; p++) {
    while (m % (p * p) === 0) {
      m /= p * p;
      k *= p;
    }
  }
  const g = gcd(k, d);
  const num = k / g;
  const den = d / g;
  const root = m === 1 ? String(num) : `${num === 1 ? "" : num}√${m}`;
  return den === 1 ? root : `${root}/${den}`;
}

export interface Measurement {
  /** length of the segment between the two points ("√13"); the same for a line is the distance between the two defining points */
  length: string;
  midpoint: string;
  /** y = mx + c or x = c */
  equation: string;
  /** true when everything above is exact (the coordinates are decimals with at most 3 digits) */
  exact: boolean;
}

const fmtNum = (v: number): string => String(parseFloat(v.toPrecision(6)));

/** Length, midpoint and equation of the line through two points, exactly when the coordinates are simple decimals. */
export function measure(p: Pt, q: Pt): Measurement {
  const fx1 = toFrac(p[0]);
  const fy1 = toFrac(p[1]);
  const fx2 = toFrac(q[0]);
  const fy2 = toFrac(q[1]);
  if (fx1 && fy1 && fx2 && fy2) {
    const dx = sub(fx2, fx1);
    const dy = sub(fy2, fy1);
    const len2 = add(mul(dx, dx), mul(dy, dy));
    const half: Frac = [1, 2];
    const mid = `(${fmtFrac(mul(add(fx1, fx2), half))}, ${fmtFrac(mul(add(fy1, fy2), half))})`;
    let equation: string;
    if (dx[0] === 0) equation = `x = ${fmtFrac(fx1)}`;
    else {
      const m = div(dy, dx);
      const c = sub(fy1, mul(m, fx1));
      const slope = m[0] === 0 ? "" : m[0] === m[1] ? "x" : m[0] === -m[1] ? "-x" : m[1] === 1 ? `${m[0]}x` : `(${fmtFrac(m)})x`;
      const intercept = c[0] === 0 ? "" : c[0] < 0 ? ` - ${fmtFrac([-c[0], c[1]])}` : slope === "" ? fmtFrac(c) : ` + ${fmtFrac(c)}`;
      equation = `y = ${slope}${intercept}` === "y = " ? "y = 0" : `y = ${slope}${intercept}`;
    }
    return { length: sqrtText(len2), midpoint: mid, equation, exact: true };
  }
  const dx = q[0] - p[0];
  const dy = q[1] - p[1];
  const m = dx === 0 ? null : dy / dx;
  return {
    length: fmtNum(Math.hypot(dx, dy)),
    midpoint: `(${fmtNum((p[0] + q[0]) / 2)}, ${fmtNum((p[1] + q[1]) / 2)})`,
    equation: m === null ? `x = ${fmtNum(p[0])}` : `y = ${fmtNum(m)}x + ${fmtNum(p[1] - m * p[0])}`,
    exact: false,
  };
}
