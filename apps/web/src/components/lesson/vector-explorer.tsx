"use client";

import { useCallback, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { rational } from "@allmaths/core";
import { t } from "@/i18n";

/**
 * Interactive plane for Module 1. Points snap to whole numbers so every value shown is exact
 * (spec section 6.4: no decimals). Modes: components of AB, sum of two vectors, coordinates in a basis.
 */

const SIZE = 360;
const RANGE = 6; // -6..6
const UNIT = SIZE / (2 * RANGE);
const toPx = (v: number): number => (v + RANGE) * UNIT;
const toPy = (v: number): number => (RANGE - v) * UNIT;

interface Pt {
  x: number;
  y: number;
}
type Mode = "components" | "sum" | "basis";
type Handle = "a" | "b";

const clamp = (n: number): number => Math.max(-RANGE, Math.min(RANGE, Math.round(n)));
const sub = (p: Pt, q: Pt): Pt => ({ x: p.x - q.x, y: p.y - q.y });
const show = (p: Pt): string => `(${p.x}, ${p.y})`;

function Vec({ children }: { children: string }) {
  return <span className="vecsym">{children}</span>;
}

function Arrow({ from, to, color, dashed = false, width = 2.5 }: { from: Pt; to: Pt; color: string; dashed?: boolean; width?: number }) {
  const x1 = toPx(from.x);
  const y1 = toPy(from.y);
  const x2 = toPx(to.x);
  const y2 = toPy(to.y);
  const len = Math.hypot(x2 - x1, y2 - y1);
  if (len < 1) return null;
  const ux = (x2 - x1) / len;
  const uy = (y2 - y1) / len;
  const head = 10;
  const bx = x2 - ux * head;
  const by = y2 - uy * head;
  return (
    <g stroke={color} fill={color} strokeWidth={width} strokeLinecap="round" opacity={dashed ? 0.7 : 1}>
      <line x1={x1} y1={y1} x2={bx} y2={by} strokeDasharray={dashed ? "6 5" : undefined} />
      <polygon points={`${x2},${y2} ${bx - uy * 5},${by + ux * 5} ${bx + uy * 5},${by - ux * 5}`} stroke="none" />
    </g>
  );
}

export function VectorExplorer({ mode }: { mode: string }) {
  const m: Mode = mode === "sum" || mode === "basis" ? mode : "components";
  const initial = {
    components: { a: { x: 1, y: 1 }, b: { x: 4, y: 3 } },
    sum: { a: { x: 3, y: 1 }, b: { x: 1, y: 3 } },
    basis: { a: { x: 0, y: 0 }, b: { x: 3, y: 1 } },
  }[m];
  const [a, setA] = useState<Pt>(initial.a);
  const [b, setB] = useState<Pt>(initial.b);
  const svgRef = useRef<SVGSVGElement>(null);
  const dragging = useRef<Handle | null>(null);

  const locate = useCallback((e: ReactPointerEvent): Pt | null => {
    const svg = svgRef.current;
    if (!svg) return null;
    const r = svg.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * SIZE;
    const py = ((e.clientY - r.top) / r.height) * SIZE;
    return { x: clamp(px / UNIT - RANGE), y: clamp(RANGE - py / UNIT) };
  }, []);

  const onMove = (e: ReactPointerEvent) => {
    if (!dragging.current) return;
    const p = locate(e);
    if (!p) return;
    if (dragging.current === "a") setA(p);
    else setB(p);
  };

  const key = (h: Handle) => (e: React.KeyboardEvent) => {
    const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
    if (!d) return;
    e.preventDefault();
    const [dx = 0, dy = 0] = d;
    const f = h === "a" ? setA : setB;
    const cur = h === "a" ? a : b;
    f({ x: clamp(cur.x + dx), y: clamp(cur.y + dy) });
  };

  const origin: Pt = { x: 0, y: 0 };
  const grid = [];
  for (let i = -RANGE; i <= RANGE; i++) {
    grid.push(
      <line key={`v${i}`} x1={toPx(i)} y1={0} x2={toPx(i)} y2={SIZE} stroke="var(--line)" strokeWidth={i === 0 ? 2 : 1} />,
      <line key={`h${i}`} x1={0} y1={toPy(i)} x2={SIZE} y2={toPy(i)} stroke="var(--line)" strokeWidth={i === 0 ? 2 : 1} />,
    );
  }

  const dot = (p: Pt, h: Handle, color: string, label: string) => (
    <g
      key={h}
      tabIndex={0}
      role="slider"
      aria-label={label}
      aria-valuetext={show(p)}
      onKeyDown={key(h)}
      onPointerDown={(e) => {
        dragging.current = h;
        (e.currentTarget as SVGGElement).setPointerCapture(e.pointerId);
      }}
      onPointerMove={onMove}
      onPointerUp={() => (dragging.current = null)}
      onPointerCancel={() => (dragging.current = null)}
      style={{ cursor: "grab", touchAction: "none" }}
    >
      <circle cx={toPx(p.x)} cy={toPy(p.y)} r={18} fill="transparent" />
      <circle cx={toPx(p.x)} cy={toPy(p.y)} r={7} fill={color} stroke="var(--surface)" strokeWidth={2} />
    </g>
  );

  let info: React.ReactNode;
  let content: React.ReactNode;

  if (m === "components") {
    const ab = sub(b, a);
    info = (
      <>
        <p>
          A = {show(a)}, B = {show(b)}
        </p>
        <p className="font-semibold">
          <Vec>AB</Vec> = ({b.x} − {a.x}, {b.y} − {a.y}) = {show(ab)}
        </p>
      </>
    );
    content = (
      <>
        <Arrow from={a} to={{ x: b.x, y: a.y }} color="var(--muted)" dashed width={1.8} />
        <Arrow from={{ x: b.x, y: a.y }} to={b} color="var(--muted)" dashed width={1.8} />
        <Arrow from={origin} to={ab} color="var(--success)" dashed width={2} />
        <Arrow from={a} to={b} color="var(--accent)" />
        {dot(a, "a", "var(--ink)", "A")}
        {dot(b, "b", "var(--accent)", "B")}
        <text x={toPx(a.x) + 10} y={toPy(a.y) - 10} fill="var(--ink)" fontSize="14" fontWeight="700">A</text>
        <text x={toPx(b.x) + 10} y={toPy(b.y) - 10} fill="var(--accent)" fontSize="14" fontWeight="700">B</text>
      </>
    );
  } else if (m === "sum") {
    const s: Pt = { x: a.x + b.x, y: a.y + b.y };
    info = (
      <>
        <p>
          <Vec>u</Vec> = {show(a)}, <Vec>v</Vec> = {show(b)}
        </p>
        <p className="font-semibold">
          <Vec>u</Vec> + <Vec>v</Vec> = {show(s)}
        </p>
      </>
    );
    content = (
      <>
        <Arrow from={a} to={s} color="var(--muted)" dashed width={1.8} />
        <Arrow from={b} to={s} color="var(--muted)" dashed width={1.8} />
        <Arrow from={origin} to={s} color="var(--success)" />
        <Arrow from={origin} to={a} color="var(--accent)" />
        <Arrow from={origin} to={b} color="var(--warning)" />
        {dot(a, "a", "var(--accent)", "u")}
        {dot(b, "b", "var(--warning)", "v")}
      </>
    );
  } else {
    const e1: Pt = { x: 1, y: 1 };
    const e2: Pt = { x: 1, y: -1 };
    // w = p e1 + q e2  =>  p = (x + y)/2, q = (x - y)/2   (exact fractions)
    const p = rational.frac(b.x + b.y, 2);
    const q = rational.frac(b.x - b.y, 2);
    info = (
      <>
        <p>
          <Vec>e₁</Vec> = (1, 1), <Vec>e₂</Vec> = (1, −1), <Vec>w</Vec> = {show(b)}
        </p>
        <p className="font-semibold">
          {t("visual.coordinates")}: ({rational.toString(p)}, {rational.toString(q)})
        </p>
      </>
    );
    const mid: Pt = { x: Number(p.num) / Number(p.den), y: Number(p.num) / Number(p.den) };
    content = (
      <>
        <Arrow from={origin} to={e1} color="var(--accent)" />
        <Arrow from={origin} to={e2} color="var(--warning)" />
        <Arrow from={origin} to={mid} color="var(--accent)" dashed width={1.8} />
        <Arrow from={mid} to={b} color="var(--warning)" dashed width={1.8} />
        <Arrow from={origin} to={b} color="var(--success)" />
        {dot(b, "b", "var(--success)", "w")}
      </>
    );
  }

  return (
    <div className="grid gap-3">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="mx-auto w-full max-w-sm touch-none rounded-[var(--radius)] border border-line bg-surface"
        role="group"
        aria-label={t("lesson.visual")}
      >
        {grid}
        {content}
      </svg>
      <div aria-live="polite" className="text-center text-[1.05rem] leading-8 tabular-nums">
        {info}
      </div>
      <p className="text-center text-sm text-muted">{t("visual.dragHint")}</p>
    </div>
  );
}
