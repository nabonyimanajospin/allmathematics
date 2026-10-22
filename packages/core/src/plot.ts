/**
 * Plotting of curves for lessons: a small, safe expression evaluator (no eval, no Function) and the sampling of
 * polar, parametric and Cartesian curves. Pure code, shared by the browser and by content verification.
 *
 * The expressions use the same notation as the rest of the platform: `^` for powers, `*` for products,
 * `pi`, `e`, and the functions sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, sqrt, exp, ln, abs.
 */

export type PlotValue = number | string | boolean;
export type PlotConfig = Record<string, PlotValue>;

const FUNCTIONS: Record<string, (x: number) => number> = {
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  asin: Math.asin,
  acos: Math.acos,
  atan: Math.atan,
  sinh: Math.sinh,
  cosh: Math.cosh,
  tanh: Math.tanh,
  sqrt: Math.sqrt,
  exp: Math.exp,
  ln: Math.log,
  abs: Math.abs,
};
const CONSTANTS: Record<string, number> = { pi: Math.PI, e: Math.E };

type Node =
  | { k: "num"; v: number }
  | { k: "var"; i: number }
  | { k: "neg"; a: Node }
  | { k: "bin"; op: "+" | "-" | "*" | "/" | "^"; a: Node; b: Node }
  | { k: "fn"; f: (x: number) => number; a: Node };

export class PlotExpressionError extends Error {}

function tokenize(src: string): string[] {
  const tokens: string[] = [];
  const re = /\s*(\d+(?:\.\d+)?|[A-Za-z_][A-Za-z_0-9]*|[-+*/^()])/gy;
  let pos = 0;
  while (pos < src.length) {
    re.lastIndex = pos;
    const m = re.exec(src);
    if (!m) {
      if (/^\s*$/.test(src.slice(pos))) break;
      throw new PlotExpressionError(`Unexpected character at “${src.slice(pos, pos + 8)}” in “${src}”`);
    }
    tokens.push(m[1]!);
    pos = re.lastIndex;
  }
  return tokens;
}

function parse(src: string, vars: readonly string[]): Node {
  const toks = tokenize(src);
  let p = 0;
  const peek = () => toks[p];
  const next = () => toks[p++];
  const fail = (msg: string): never => {
    throw new PlotExpressionError(`${msg} in “${src}”`);
  };

  const primary = (): Node => {
    const t = next();
    if (t === undefined) return fail("The expression ends too early");
    if (/^\d/.test(t)) return { k: "num", v: Number(t) };
    if (t === "(") {
      const inner = sum();
      if (next() !== ")") return fail("Missing )");
      return inner;
    }
    if (/^[A-Za-z_]/.test(t)) {
      if (peek() === "(") {
        const f = Object.hasOwn(FUNCTIONS, t) ? FUNCTIONS[t] : undefined;
        if (!f) return fail(`Unknown function ${t}`);
        next();
        const arg = sum();
        if (next() !== ")") return fail("Missing )");
        return { k: "fn", f, a: arg };
      }
      const vi = vars.indexOf(t);
      if (vi >= 0) return { k: "var", i: vi };
      if (Object.hasOwn(CONSTANTS, t)) return { k: "num", v: CONSTANTS[t]! };
      return fail(`Unknown name ${t}`);
    }
    return fail(`Unexpected ${t}`);
  };
  // power is right-associative and binds tighter than a unary minus on its left: -x^2 = -(x^2)
  const power = (): Node => {
    const base = primary();
    if (peek() === "^") {
      next();
      return { k: "bin", op: "^", a: base, b: unary() };
    }
    return base;
  };
  const unary = (): Node => {
    if (peek() === "-") {
      next();
      return { k: "neg", a: unary() };
    }
    if (peek() === "+") {
      next();
      return unary();
    }
    return power();
  };
  const product = (): Node => {
    let a = unary();
    while (peek() === "*" || peek() === "/") {
      const op = next() as "*" | "/";
      a = { k: "bin", op, a, b: unary() };
    }
    return a;
  };
  const sum = (): Node => {
    let a = product();
    while (peek() === "+" || peek() === "-") {
      const op = next() as "+" | "-";
      a = { k: "bin", op, a, b: product() };
    }
    return a;
  };
  const tree = sum();
  if (p < toks.length) fail(`Unexpected ${toks[p]}`);
  return tree;
}

function run(n: Node, args: readonly number[]): number {
  switch (n.k) {
    case "num":
      return n.v;
    case "var":
      return args[n.i]!;
    case "neg":
      return -run(n.a, args);
    case "fn":
      return n.f(run(n.a, args));
    case "bin": {
      const a = run(n.a, args);
      const b = run(n.b, args);
      switch (n.op) {
        case "+":
          return a + b;
        case "-":
          return a - b;
        case "*":
          return a * b;
        case "/":
          return a / b;
        case "^":
          return Math.pow(a, b);
      }
    }
  }
}

/** Compile an expression of the given variables into a function. Throws PlotExpressionError on bad input. */
export function compileExpr(src: string, vars: readonly string[] = []): (...args: number[]) => number {
  const tree = parse(src, vars);
  return (...args: number[]) => run(tree, args);
}

// --- curves --------------------------------------------------------------------------------------------
export type PlotMode = "polar" | "parametric" | "cartesian";
export interface Curve {
  label: string;
  /** Drawn as a dashed line (an asymptote, an axis of symmetry). */
  dashed: boolean;
  /** Pieces of the curve: a piece is broken where the function is undefined or jumps off the picture. */
  pieces: [number, number][][];
}
export interface Plot {
  mode: PlotMode;
  curves: Curve[];
  xmin: number;
  xmax: number;
  ymin: number;
  ymax: number;
}

const num = (c: PlotConfig, key: string, dflt: number): number => {
  const v = c[key];
  if (v === undefined) return dflt;
  if (typeof v === "number") return v;
  if (typeof v === "string") {
    const f = compileExpr(v);
    const r = f();
    if (!Number.isFinite(r)) throw new PlotExpressionError(`“${v}” is not a number`);
    return r;
  }
  throw new PlotExpressionError(`${key} must be a number`);
};

const SAMPLES = 1200;

/** Sample the curves of a plot block. Throws PlotExpressionError when the configuration is wrong. */
export function buildPlot(config: PlotConfig): Plot {
  const mode = config.mode;
  if (mode !== "polar" && mode !== "parametric" && mode !== "cartesian") throw new PlotExpressionError("mode must be polar, parametric or cartesian");
  const half = num(config, "range", 6);
  const xmin = num(config, "xmin", -half);
  const xmax = num(config, "xmax", half);
  const ymin = num(config, "ymin", -half);
  const ymax = num(config, "ymax", half);
  const tmin = num(config, "tmin", mode === "cartesian" ? xmin : 0);
  const tmax = num(config, "tmax", mode === "cartesian" ? xmax : 2 * Math.PI);
  if (!(tmax > tmin)) throw new PlotExpressionError("tmax must be larger than tmin");

  const specs: { label: string; dashed: boolean; fx: (t: number) => number; fy: (t: number) => number }[] = [];
  for (const suffix of ["", "2", "3", "4", "5"]) {
    const label = String(config[`l${suffix || "1"}`] ?? "");
    const dashed = config[`dash${suffix || "1"}`] === true;
    if (mode === "polar") {
      const src = config[`r${suffix}`];
      if (typeof src !== "string") continue;
      const r = compileExpr(src, ["t"]);
      specs.push({ label, dashed, fx: (t) => r(t) * Math.cos(t), fy: (t) => r(t) * Math.sin(t) });
    } else if (mode === "parametric") {
      const sx = config[`x${suffix}`];
      const sy = config[`y${suffix}`];
      if (typeof sx !== "string" || typeof sy !== "string") continue;
      specs.push({ label, dashed, fx: compileExpr(sx, ["t"]), fy: compileExpr(sy, ["t"]) });
    } else {
      const src = config[`f${suffix}`];
      if (typeof src !== "string") continue;
      specs.push({ label, dashed, fx: (t) => t, fy: compileExpr(src, ["x"]) });
    }
  }
  if (specs.length === 0) throw new PlotExpressionError("A plot needs at least one curve");

  const spanX = xmax - xmin;
  const spanY = ymax - ymin;
  const curves = specs.map((s) => {
    const pieces: [number, number][][] = [];
    let cur: [number, number][] = [];
    let last: [number, number] | null = null;
    const at = (t: number): [number, number] | null => {
      const x = s.fx(t);
      const y = s.fy(t);
      return Number.isFinite(x) && Number.isFinite(y) ? [x, y] : null;
    };
    /** Between a defined and an undefined parameter, find (by bisection) the edge of the domain: the curve then reaches its true end. */
    const edge = (good: number, bad: number): [number, number] | null => {
      let a = good;
      let b = bad;
      for (let k = 0; k < 40; k++) {
        const m = (a + b) / 2;
        if (at(m)) a = m;
        else b = m;
      }
      return at(a);
    };
    let prevT = tmin;
    let prev: [number, number] | null = null;
    for (let i = 0; i <= SAMPLES; i++) {
      const t = tmin + ((tmax - tmin) * i) / SAMPLES;
      const pt = at(t);
      if (pt === null && prev !== null) {
        const e = edge(prevT, t);
        if (e) cur.push(e);
      } else if (pt !== null && prev === null && i > 0) {
        const e = edge(t, prevT);
        if (e) cur.push(e);
      }
      const visible = pt !== null && Math.abs(pt[0]) < 50 * spanX && Math.abs(pt[1]) < 50 * spanY;
      // a jump of more than a quarter of the picture between two samples is an asymptote, not a line
      const jump = visible && last !== null && (Math.abs(pt[0] - last[0]) > spanX / 4 || Math.abs(pt[1] - last[1]) > spanY / 4);
      if (!visible || jump || pt === null) {
        if (cur.length > 1) pieces.push(cur);
        cur = [];
      }
      if (visible && pt !== null) {
        cur.push(pt);
        last = pt;
      } else last = null;
      prev = pt;
      prevT = t;
    }
    if (cur.length > 1) pieces.push(cur);
    return { label: s.label, dashed: s.dashed, pieces };
  });
  return { mode, curves, xmin, xmax, ymin, ymax };
}

/** A message when the configuration of a plot block is wrong, else null. */
export function validatePlotConfig(config: PlotConfig): string | null {
  try {
    const plot = buildPlot(config);
    for (const c of plot.curves) {
      const points = c.pieces.reduce((n, p) => n + p.length, 0);
      if (points < 20) return `A curve has fewer than 20 visible points (${points}): check the expression and the range.`;
    }
    return null;
  } catch (e) {
    return e instanceof PlotExpressionError ? e.message : String(e);
  }
}
