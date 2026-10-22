/**
 * Geometry figures: points, segments, lines, polygons and circles in the plane (2D) or in space (3D), described in the lesson
 * file with exact coordinates (whole numbers, fractions such as 19/3, radicals such as sqrt(2)).
 * The browser draws them; this module reads the description and projects 3D points on the screen.
 */

import { compileExpr } from "./plot";

export type Coord = number | string;
export type FigPoint = Coord[];
/** A point given by its id, or by its coordinates. */
export type Ref = string | FigPoint;
export type FigColor = "accent" | "warning" | "success" | "danger" | "ink" | "muted";

export type FigureItem =
  | { t: "point"; id: string; at: FigPoint; label?: string; color?: FigColor }
  | { t: "segment"; from: Ref; to: Ref; dashed?: boolean; color?: FigColor; label?: string; arrow?: boolean }
  | { t: "line"; through: [Ref, Ref]; dashed?: boolean; color?: FigColor; label?: string }
  | { t: "polygon"; pts: Ref[]; fill?: FigColor; color?: FigColor }
  | { t: "circle"; center: Ref; r: Coord; dashed?: boolean; color?: FigColor }
  | { t: "right"; at: Ref; a: Ref; b: Ref }
  | { t: "text"; at: Ref; text: string; color?: FigColor };

export interface Figure {
  dim: 2 | 3;
  alt: string;
  /** 2D: [xmin, xmax, ymin, ymax]. 3D: the half-size of the box shown. */
  view: number[];
  axes?: boolean;
  items: FigureItem[];
}

export class FigureError extends Error {}

const num = (c: Coord): number => {
  if (typeof c === "number") return c;
  try {
    const v = compileExpr(c, [])();
    if (!Number.isFinite(v)) throw new FigureError(`not a number: ${c}`);
    return v;
  } catch {
    throw new FigureError(`cannot read the coordinate “${c}”`);
  }
};

export type P2 = [number, number];
export type P3 = [number, number, number];

/** Numeric coordinates of every named point. */
export function pointTable(fig: Figure): Map<string, number[]> {
  const out = new Map<string, number[]>();
  for (const it of fig.items) {
    if (it.t !== "point") continue;
    if (out.has(it.id)) throw new FigureError(`the point id ${it.id} is used twice`);
    if (it.at.length !== fig.dim) throw new FigureError(`the point ${it.id} needs ${fig.dim} coordinates`);
    out.set(it.id, it.at.map(num));
  }
  return out;
}

export function resolveRef(fig: Figure, table: Map<string, number[]>, r: Ref): number[] {
  if (typeof r === "string") {
    const p = table.get(r);
    if (!p) throw new FigureError(`unknown point ${r}`);
    return p;
  }
  if (r.length !== fig.dim) throw new FigureError(`a point of this figure needs ${fig.dim} coordinates`);
  return r.map(num);
}

export function radius(c: Coord): number {
  return num(c);
}

/** A reason why the figure cannot be drawn, or null. */
export function validateFigure(fig: Figure): string | null {
  try {
    if (fig.dim === 2 && fig.view.length !== 4) return "a 2D figure needs view: [xmin, xmax, ymin, ymax]";
    if (fig.dim === 3 && fig.view.length !== 1) return "a 3D figure needs view: [half-size]";
    const table = pointTable(fig);
    for (const it of fig.items) {
      if (it.t === "segment") {
        resolveRef(fig, table, it.from);
        resolveRef(fig, table, it.to);
      } else if (it.t === "line") {
        if (fig.dim !== 2) return "a line (unbounded) is only for 2D figures; use a segment in 3D";
        resolveRef(fig, table, it.through[0]);
        resolveRef(fig, table, it.through[1]);
      } else if (it.t === "polygon") {
        if (it.pts.length < 3) return "a polygon needs at least three points";
        it.pts.forEach((p) => resolveRef(fig, table, p));
      } else if (it.t === "circle") {
        resolveRef(fig, table, it.center);
        if (!(num(it.r) > 0)) return "a circle needs a positive radius";
      } else if (it.t === "right") {
        resolveRef(fig, table, it.at);
        resolveRef(fig, table, it.a);
        resolveRef(fig, table, it.b);
      } else if (it.t === "text") {
        resolveRef(fig, table, it.at);
      }
    }
    return null;
  } catch (e) {
    return e instanceof Error ? e.message : String(e);
  }
}

/** The 3D rotation: yaw about the vertical (z) axis, then pitch (tilt towards the viewer). Returns screen x, screen y (up) and depth. */
export function project3(p: number[], yaw: number, pitch: number): { x: number; y: number; depth: number } {
  const [x = 0, y = 0, z = 0] = p;
  const cy = Math.cos(yaw);
  const sy = Math.sin(yaw);
  const cp = Math.cos(pitch);
  const sp = Math.sin(pitch);
  // rotate about z
  const x1 = x * cy - y * sy;
  const y1 = x * sy + y * cy;
  // tilt: the screen's up is a mix of z and the depth axis
  return { x: x1, y: z * cp + y1 * sp, depth: y1 * cp - z * sp };
}
