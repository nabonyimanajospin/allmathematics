"use client";

import { useRef, useState, type PointerEvent as ReactPointerEvent, type ReactNode } from "react";
import { pointTable, project3, radius, resolveRef, validateFigure, type FigColor, type Figure, type FigureItem } from "@allmaths/core";
import { t } from "@/i18n";

const W = 460;
const PAD = 30;
const COLOR: Record<FigColor, string> = {
  accent: "var(--accent)",
  warning: "var(--warning)",
  success: "var(--success)",
  danger: "var(--danger)",
  ink: "var(--ink)",
  muted: "var(--muted)",
};
const colorOf = (c: FigColor | undefined, fallback: FigColor = "ink"): string => COLOR[c ?? fallback];

/** "M_a" is drawn as M with a small subscript a. */
function Name({ x, y, text, color, size = 15, anchor = "middle" }: { x: number; y: number; text: string; color: string; size?: number; anchor?: "start" | "middle" | "end" }) {
  const [main, sub] = text.split("_");
  return (
    <text
      x={x}
      y={y}
      textAnchor={anchor}
      dominantBaseline="middle"
      fontSize={size}
      fontWeight={700}
      fill={color}
      stroke="var(--surface)"
      strokeWidth={4}
      paintOrder="stroke"
      style={{ userSelect: "none" }}
    >
      {main}
      {sub ? (
        <tspan fontSize={size * 0.72} dy={size * 0.28}>
          {sub}
        </tspan>
      ) : null}
    </text>
  );
}

type Screen = (p: number[]) => { x: number; y: number; depth: number };

function ticks(min: number, max: number): number[] {
  const span = max - min;
  const step = span <= 12 ? 1 : span <= 24 ? 2 : span <= 60 ? 5 : 10;
  const out: number[] = [];
  for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) out.push(v);
  return out;
}

/** The part of the infinite line through p and q that lies inside the view rectangle, or null. */
function clipLine(p: number[], q: number[], [x0, x1, y0, y1]: number[]): [number[], number[]] | null {
  const dx = q[0]! - p[0]!;
  const dy = q[1]! - p[1]!;
  if (dx === 0 && dy === 0) return null;
  let lo = -Infinity;
  let hi = Infinity;
  const cut = (pos: number, d: number, min: number, max: number): boolean => {
    if (d === 0) return pos >= min && pos <= max;
    const a = (min - pos) / d;
    const b = (max - pos) / d;
    lo = Math.max(lo, Math.min(a, b));
    hi = Math.min(hi, Math.max(a, b));
    return true;
  };
  if (!cut(p[0]!, dx, x0!, x1!) || !cut(p[1]!, dy, y0!, y1!) || lo > hi) return null;
  return [[p[0]! + lo * dx, p[1]! + lo * dy], [p[0]! + hi * dx, p[1]! + hi * dy]];
}

export function FigureExplorer({ figure }: { figure: Figure }) {
  const problem = validateFigure(figure);
  const [yaw, setYaw] = useState(-0.62);
  const [pitch, setPitch] = useState(0.42);
  const drag = useRef<{ x: number; y: number; yaw: number; pitch: number } | null>(null);
  if (problem) return <p role="alert" className="text-warning">{problem}</p>;

  const is3 = figure.dim === 3;
  const table = pointTable(figure);
  const ref = (r: Parameters<typeof resolveRef>[2]) => resolveRef(figure, table, r);

  // --- the screen mapping ---------------------------------------------------------------------------------------
  let width: number;
  let height: number;
  let screen: Screen;
  let unit3 = 1;
  if (is3) {
    // the figure is centred on the middle of its points and scaled to fill the frame, whatever it looks like
    const all = [...table.values()];
    const lo = [0, 1, 2].map((k) => Math.min(0, ...all.map((p) => p[k]!)));
    const hi = [0, 1, 2].map((k) => Math.max(0, ...all.map((p) => p[k]!)));
    const mid = [0, 1, 2].map((k) => (lo[k]! + hi[k]!) / 2);
    // the farthest point from the middle, so that the figure fits in the frame in every position
    let extent = Math.max(0.5, ...all.map((p) => Math.hypot(...p.map((v, k) => v - mid[k]!))));
    for (const it of figure.items) if (it.t === "circle") extent = Math.max(extent, radius(it.r) + Math.hypot(...resolveRef(figure, table, it.center).map((v, k) => v - mid[k]!)));
    unit3 = (W * 0.43 - PAD) / (extent * 1.1);
    width = W;
    height = W * 0.92;
    screen = (p) => {
      const q = project3(p.map((v, k) => v - mid[k]!), yaw, pitch);
      return { x: width / 2 + q.x * unit3, y: height / 2 - q.y * unit3, depth: q.depth };
    };
  } else {
    const [x0, x1, y0, y1] = figure.view as [number, number, number, number];
    const scale = (W - 2 * PAD) / Math.max(x1 - x0, y1 - y0);
    width = (x1 - x0) * scale + 2 * PAD;
    height = (y1 - y0) * scale + 2 * PAD;
    screen = (p) => ({ x: PAD + (p[0]! - x0) * scale, y: PAD + (y1 - p[1]!) * scale, depth: 0 });
  }
  const unit = is3 ? unit3 : (W - 2 * PAD) / Math.max(figure.view[1]! - figure.view[0]!, figure.view[3]! - figure.view[2]!);

  // labels are pushed away from the middle of the figure
  const pts = [...table.values()].map((p) => screen(p));
  const cx = pts.length ? pts.reduce((a, p) => a + p.x, 0) / pts.length : width / 2;
  const cy = pts.length ? pts.reduce((a, p) => a + p.y, 0) / pts.length : height / 2;
  const away = (x: number, y: number, d = 15): { x: number; y: number } => {
    const dx = x - cx;
    const dy = y - cy;
    const l = Math.hypot(dx, dy) || 1;
    return { x: x + (dx / l) * d, y: y + (dy / l) * d };
  };

  // --- axes --------------------------------------------------------------------------------------------------------
  const axes: ReactNode[] = [];
  if (figure.axes !== false) {
    if (is3) {
      const h = Math.max(figure.view[0]!, 1);
      const names: [string, number[]][] = [["x", [h, 0, 0]], ["y", [0, h, 0]], ["z", [0, 0, h]]];
      for (const [n, end] of names) {
        const a = screen(end.map((v) => -v * 0.0));
        const b = screen(end);
        axes.push(
          <line key={`ax${n}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="var(--muted)" strokeWidth={1.4} />,
          <text key={`an${n}`} x={b.x + (b.x - a.x) * 0.06 + 4} y={b.y + (b.y - a.y) * 0.06} fontSize={13} fontStyle="italic" fill="var(--ink)">
            {n}
          </text>,
        );
      }
    } else {
      const [x0, x1, y0, y1] = figure.view as [number, number, number, number];
      for (const v of ticks(x0, x1)) {
        const a = screen([v, y0]);
        const b = screen([v, y1]);
        axes.push(<line key={`gx${v}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="var(--line)" strokeWidth={v === 0 ? 0 : 1} />);
      }
      for (const v of ticks(y0, y1)) {
        const a = screen([x0, v]);
        const b = screen([x1, v]);
        axes.push(<line key={`gy${v}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="var(--line)" strokeWidth={v === 0 ? 0 : 1} />);
      }
      const ox = Math.min(Math.max(0, x0), x1);
      const oy = Math.min(Math.max(0, y0), y1);
      const ax0 = screen([x0, oy]);
      const ax1 = screen([x1, oy]);
      const ay0 = screen([ox, y0]);
      const ay1 = screen([ox, y1]);
      axes.push(
        <line key="axx" x1={ax0.x} y1={ax0.y} x2={ax1.x} y2={ax1.y} stroke="var(--ink)" strokeWidth={1.4} opacity={0.75} />,
        <line key="axy" x1={ay0.x} y1={ay0.y} x2={ay1.x} y2={ay1.y} stroke="var(--ink)" strokeWidth={1.4} opacity={0.75} />,
        <text key="lx" x={ax1.x - 6} y={ax1.y - 8} fontSize={13} fontStyle="italic" fill="var(--ink)">
          x
        </text>,
        <text key="ly" x={ay1.x + 8} y={ay1.y + 12} fontSize={13} fontStyle="italic" fill="var(--ink)">
          y
        </text>,
      );
      for (const v of ticks(x0, x1)) {
        if (v === 0) continue;
        const p = screen([v, oy]);
        axes.push(
          <text key={`tx${v}`} x={p.x} y={p.y + 14} textAnchor="middle" fontSize={10} fill="var(--muted)">
            {v}
          </text>,
        );
      }
      for (const v of ticks(y0, y1)) {
        if (v === 0) continue;
        const p = screen([ox, v]);
        axes.push(
          <text key={`ty${v}`} x={p.x - 6} y={p.y + 3.5} textAnchor="end" fontSize={10} fill="var(--muted)">
            {v}
          </text>,
        );
      }
      const o = screen([ox, oy]);
      axes.push(
        <text key="o" x={o.x - 8} y={o.y + 13} textAnchor="end" fontSize={11} fontWeight={700} fill="var(--ink)">
          O
        </text>,
      );
    }
  }

  // --- items ---------------------------------------------------------------------------------------------------------
  const polygons: { depth: number; node: ReactNode }[] = [];
  const lines: ReactNode[] = [];
  const marks: ReactNode[] = [];
  const dots: ReactNode[] = [];
  const labels: ReactNode[] = [];

  figure.items.forEach((it: FigureItem, i: number) => {
    if (it.t === "polygon") {
      const ps = it.pts.map((r) => screen(ref(r)));
      const depth = ps.reduce((a, p) => a + p.depth, 0) / ps.length;
      polygons.push({
        depth,
        node: (
          <polygon
            key={i}
            points={ps.map((p) => `${p.x},${p.y}`).join(" ")}
            fill={colorOf(it.fill ?? it.color, "accent")}
            fillOpacity={it.fill ? 0.14 : 0}
            stroke={colorOf(it.color, "accent")}
            strokeWidth={2.4}
            strokeLinejoin="round"
          />
        ),
      });
    } else if (it.t === "circle") {
      const c = screen(ref(it.center));
      const r = radius(it.r) * unit;
      lines.push(
        <circle
          key={i}
          cx={c.x}
          cy={c.y}
          r={r}
          fill={is3 ? "var(--accent)" : "none"}
          fillOpacity={is3 ? 0.07 : 0}
          stroke={colorOf(it.color, "accent")}
          strokeWidth={2.2}
          strokeDasharray={it.dashed ? "6 5" : undefined}
        />,
      );
    } else if (it.t === "segment") {
      const a = screen(ref(it.from));
      const b = screen(ref(it.to));
      const col = colorOf(it.color, "accent");
      lines.push(<line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={col} strokeWidth={2.4} strokeLinecap="round" strokeDasharray={it.dashed ? "6 5" : undefined} />);
      if (it.arrow) {
        const len = Math.hypot(b.x - a.x, b.y - a.y) || 1;
        const ux = (b.x - a.x) / len;
        const uy = (b.y - a.y) / len;
        lines.push(<polygon key={`h${i}`} points={`${b.x},${b.y} ${b.x - ux * 12 - uy * 5},${b.y - uy * 12 + ux * 5} ${b.x - ux * 12 + uy * 5},${b.y - uy * 12 - ux * 5}`} fill={col} />);
      }
      if (it.label) {
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        const len = Math.hypot(b.x - a.x, b.y - a.y) || 1;
        // on the side of the segment that faces away from the middle of the figure
        const nx = -(b.y - a.y) / len;
        const ny = (b.x - a.x) / len;
        const side = (mx - cx) * nx + (my - cy) * ny >= 0 ? 1 : -1;
        labels.push(<Name key={`s${i}`} x={mx + nx * side * 13} y={my + ny * side * 13} text={it.label} color={col} size={13} />);
      }
    } else if (it.t === "line") {
      const p = ref(it.through[0]);
      const q = ref(it.through[1]);
      const seg = clipLine(p, q, figure.view);
      if (seg) {
        const a = screen(seg[0]);
        const b = screen(seg[1]);
        const col = colorOf(it.color, "accent");
        lines.push(<line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={col} strokeWidth={2.4} strokeLinecap="round" strokeDasharray={it.dashed ? "6 5" : undefined} />);
        if (it.label) labels.push(<Name key={`l${i}`} x={b.x - 6} y={b.y + (b.y > height / 2 ? -14 : 14)} text={it.label} color={col} size={13} anchor="end" />);
      }
    } else if (it.t === "right") {
      const o = screen(ref(it.at));
      const a = screen(ref(it.a));
      const b = screen(ref(it.b));
      const la = Math.hypot(a.x - o.x, a.y - o.y) || 1;
      const lb = Math.hypot(b.x - o.x, b.y - o.y) || 1;
      const s = 11;
      const ax = ((a.x - o.x) / la) * s;
      const ay = ((a.y - o.y) / la) * s;
      const bx = ((b.x - o.x) / lb) * s;
      const by = ((b.y - o.y) / lb) * s;
      marks.push(<polyline key={i} points={`${o.x + ax},${o.y + ay} ${o.x + ax + bx},${o.y + ay + by} ${o.x + bx},${o.y + by}`} fill="none" stroke="var(--ink)" strokeWidth={1.4} />);
    } else if (it.t === "text") {
      const p = screen(ref(it.at));
      labels.push(<Name key={`t${i}`} x={p.x} y={p.y} text={it.text} color={colorOf(it.color)} size={13} />);
    } else if (it.t === "point") {
      const p = screen(table.get(it.id)!);
      const col = colorOf(it.color, "ink");
      dots.push(<circle key={i} cx={p.x} cy={p.y} r={5} fill={col} stroke="var(--surface)" strokeWidth={2} />);
      const name = it.label ?? it.id;
      if (name !== "") {
        const l = away(p.x, p.y);
        labels.push(<Name key={`p${i}`} x={l.x} y={l.y} text={name} color={col} />);
      }
    }
  });
  polygons.sort((a, b) => b.depth - a.depth);

  // --- turning the 3D view ---------------------------------------------------------------------------------------------
  const down = (e: ReactPointerEvent<SVGSVGElement>) => {
    if (!is3) return;
    drag.current = { x: e.clientX, y: e.clientY, yaw, pitch };
    (e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId);
  };
  const move = (e: ReactPointerEvent<SVGSVGElement>) => {
    const d = drag.current;
    if (!d) return;
    setYaw(d.yaw + (e.clientX - d.x) * 0.01);
    setPitch(Math.max(-1.2, Math.min(1.45, d.pitch + (e.clientY - d.y) * 0.01)));
  };
  const key = (e: React.KeyboardEvent) => {
    if (!is3) return;
    const step = 0.12;
    if (e.key === "ArrowLeft") setYaw((v) => v - step);
    else if (e.key === "ArrowRight") setYaw((v) => v + step);
    else if (e.key === "ArrowUp") setPitch((v) => Math.min(1.45, v + step));
    else if (e.key === "ArrowDown") setPitch((v) => Math.max(-1.2, v - step));
    else return;
    e.preventDefault();
  };

  return (
    <figure>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={figure.alt}
        tabIndex={is3 ? 0 : undefined}
        onKeyDown={key}
        onPointerDown={down}
        onPointerMove={move}
        onPointerUp={() => (drag.current = null)}
        onPointerCancel={() => (drag.current = null)}
        className={`mx-auto block w-full max-w-[30rem] rounded-[var(--radius-sm)] bg-surface ${is3 ? "cursor-grab touch-none" : ""}`}
      >
        {axes}
        {polygons.map((p) => p.node)}
        {lines}
        {marks}
        {dots}
        {labels}
      </svg>
      {is3 ? (
        <div className="mt-2 flex items-center justify-center gap-3 text-sm text-muted">
          <span>{t("visual.rotateHint")}</span>
          <button
            type="button"
            onClick={() => {
              setYaw(-0.62);
              setPitch(0.42);
            }}
            className="min-h-9 rounded-[var(--radius-sm)] border border-line bg-surface-2 px-3 font-semibold text-ink hover:bg-accent-soft"
          >
            {t("visual.resetView")}
          </button>
        </div>
      ) : null}
    </figure>
  );
}
