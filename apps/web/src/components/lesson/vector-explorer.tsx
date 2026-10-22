"use client";

import { useCallback, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { rational } from "@allmaths/core";
import { t } from "@/i18n";

/**
 * Interactive plane for Module 1. Points snap to whole numbers so every value shown is exact
 * (spec section 6.4: no decimals). Modes: components of AB, sum of two vectors, coordinates in a basis.
 * Points are written in a row, vectors as columns.
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
const showPoint = (p: Pt): string => `(${p.x}, ${p.y})`;

/** A vector name with its arrow, as in print. */
function Vec({ children }: { children: string }) {
  return <span className="vecsym">{children}</span>;
}

/** The components of a vector, written as a column. */
function Col({ x, y }: { x: string | number; y: string | number }) {
  return (
    <span className="colvec" aria-label={`(${x}, ${y})`} role="img">
      <span>{x}</span>
      <span>{y}</span>
    </span>
  );
}

/** An arrow with a clear head. */
function Arrow({ from, to, color, dashed = false, width = 2.5, opacity = 1 }: { from: Pt; to: Pt; color: string; dashed?: boolean; width?: number; opacity?: number }) {
  const x1 = toPx(from.x);
  const y1 = toPy(from.y);
  const x2 = toPx(to.x);
  const y2 = toPy(to.y);
  const len = Math.hypot(x2 - x1, y2 - y1);
  if (len < 1) return null;
  const ux = (x2 - x1) / len;
  const uy = (y2 - y1) / len;
  const head = Math.min(13, len * 0.5);
  const half = head * 0.38;
  const bx = x2 - ux * head;
  const by = y2 - uy * head;
  return (
    <g stroke={color} fill={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" opacity={opacity}>
      <line x1={x1} y1={y1} x2={bx} y2={by} strokeDasharray={dashed ? "6 5" : undefined} />
      <polygon points={`${x2},${y2} ${bx - uy * half},${by + ux * half} ${bx + uy * half},${by - ux * half}`} strokeWidth={1} />
    </g>
  );
}

/** A label that stays readable over the grid (white halo). `arrow` draws the vector arrow above the letters. */
function Label({ x, y, children, color, arrow = false, size = 15 }: { x: number; y: number; children: string; color: string; arrow?: boolean; size?: number }) {
  const w = children.length * size * 0.62;
  return (
    <g>
      <text
        x={x}
        y={y}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={size}
        fontWeight={700}
        fill={color}
        stroke="var(--surface)"
        strokeWidth={4}
        paintOrder="stroke"
        style={{ fontFamily: "var(--font-sans, system-ui)", userSelect: "none" }}
      >
        {children}
      </text>
      {arrow ? (
        <g stroke={color} fill="none" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
          <line x1={x - w / 2} y1={y - size * 0.72} x2={x + w / 2} y2={y - size * 0.72} />
          <polyline points={`${x + w / 2 - 3.5},${y - size * 0.72 - 3} ${x + w / 2},${y - size * 0.72} ${x + w / 2 - 3.5},${y - size * 0.72 + 3}`} />
        </g>
      ) : null}
    </g>
  );
}

/** Position of a label next to the middle of a segment, pushed away from it on the given side. */
function beside(from: Pt, to: Pt, offset: number, side: 1 | -1 = 1): { x: number; y: number } {
  const x1 = toPx(from.x);
  const y1 = toPy(from.y);
  const x2 = toPx(to.x);
  const y2 = toPy(to.y);
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const len = Math.hypot(x2 - x1, y2 - y1) || 1;
  return { x: mx + (side * (y2 - y1) * offset) / len, y: my - (side * (x2 - x1) * offset) / len };
}

function Axes() {
  const lines = [];
  const ticks = [];
  for (let i = -RANGE; i <= RANGE; i++) {
    if (i !== 0) {
      lines.push(
        <line key={`v${i}`} x1={toPx(i)} y1={0} x2={toPx(i)} y2={SIZE} stroke="var(--line)" strokeWidth={1} />,
        <line key={`h${i}`} x1={0} y1={toPy(i)} x2={SIZE} y2={toPy(i)} stroke="var(--line)" strokeWidth={1} />,
      );
      if (i > -RANGE && i < RANGE) {
        ticks.push(
          <text key={`tx${i}`} x={toPx(i)} y={toPy(0) + 14} textAnchor="middle" fontSize={10} fill="var(--muted)">
            {i}
          </text>,
          <text key={`ty${i}`} x={toPx(0) - 6} y={toPy(i) + 3.5} textAnchor="end" fontSize={10} fill="var(--muted)">
            {i}
          </text>,
        );
      }
    }
  }
  const o = { x: 0, y: 0 };
  return (
    <g>
      {lines}
      <Arrow from={{ x: -RANGE, y: 0 }} to={{ x: RANGE, y: 0 }} color="var(--ink)" width={1.4} opacity={0.75} />
      <Arrow from={{ x: 0, y: -RANGE }} to={{ x: 0, y: RANGE }} color="var(--ink)" width={1.4} opacity={0.75} />
      {ticks}
      <text x={SIZE - 10} y={toPy(0) - 8} fontSize={13} fontStyle="italic" fill="var(--ink)">
        x
      </text>
      <text x={toPx(0) + 9} y={12} fontSize={13} fontStyle="italic" fill="var(--ink)">
        y
      </text>
      <text x={toPx(o.x) - 9} y={toPy(o.y) + 14} textAnchor="end" fontSize={12} fontWeight={700} fill="var(--ink)">
        O
      </text>
    </g>
  );
}

export function VectorExplorer({ mode }: { mode: string }) {
  const m: Mode = mode === "sum" || mode === "basis" ? mode : "components";
  const initial = {
    components: { a: { x: 3, y: 1 }, b: { x: 1, y: 4 } },
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

  const dot = (p: Pt, h: Handle, color: string, label: string) => (
    <g
      key={h}
      tabIndex={0}
      role="slider"
      aria-label={label}
      aria-valuetext={showPoint(p)}
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
      <circle cx={toPx(p.x)} cy={toPy(p.y)} r={6.5} fill={color} stroke="var(--surface)" strokeWidth={2.5} />
    </g>
  );

  let info: React.ReactNode;
  let content: React.ReactNode;

  if (m === "components") {
    const ab = sub(b, a);
    const corner: Pt = { x: b.x, y: a.y };
    // the label of a point goes on the side away from the segment
    const away = (p: Pt, q: Pt): { x: number; y: number } => {
      const dx = toPx(p.x) - toPx(q.x);
      const dy = toPy(p.y) - toPy(q.y);
      const l = Math.hypot(dx, dy) || 1;
      return { x: toPx(p.x) + (dx / l) * 16, y: toPy(p.y) + (dy / l) * 16 };
    };
    const la = away(a, b);
    const lb = away(b, a);
    info = (
      <>
        <p>
          A {showPoint(a)} <span className="text-muted">·</span> B {showPoint(b)}
        </p>
        <p className="font-semibold">
          <Vec>AB</Vec> = <Vec>OB</Vec> − <Vec>OA</Vec> = <Col x={b.x} y={b.y} /> − <Col x={a.x} y={a.y} /> = <Col x={ab.x} y={ab.y} />
        </p>
      </>
    );
    content = (
      <>
        <Arrow from={origin} to={a} color="var(--muted)" width={1.8} opacity={0.8} />
        <Arrow from={origin} to={b} color="var(--muted)" width={1.8} opacity={0.8} />
        {(() => {
          const oa = beside(origin, a, 16, 1);
          const ob = beside(origin, b, 16, -1);
          return (
            <>
              {a.x !== 0 || a.y !== 0 ? (
                <Label x={oa.x} y={oa.y} color="var(--muted)" arrow size={12}>
                  OA
                </Label>
              ) : null}
              {b.x !== 0 || b.y !== 0 ? (
                <Label x={ob.x} y={ob.y} color="var(--muted)" arrow size={12}>
                  OB
                </Label>
              ) : null}
            </>
          );
        })()}
        {Math.abs(ab.x) > 0 && Math.abs(ab.y) > 0 ? (
          <>
            <line x1={toPx(a.x)} y1={toPy(a.y)} x2={toPx(corner.x)} y2={toPy(corner.y)} stroke="var(--success)" strokeWidth={1.8} strokeDasharray="5 4" />
            <line x1={toPx(corner.x)} y1={toPy(corner.y)} x2={toPx(b.x)} y2={toPy(b.y)} stroke="var(--success)" strokeWidth={1.8} strokeDasharray="5 4" />
            <Label x={(toPx(a.x) + toPx(corner.x)) / 2} y={toPy(a.y) + (ab.y > 0 ? 14 : -14)} color="var(--success)" size={13}>
              {String(ab.x)}
            </Label>
            <Label x={toPx(corner.x) + (ab.x > 0 ? 14 : -14)} y={(toPy(corner.y) + toPy(b.y)) / 2} color="var(--success)" size={13}>
              {String(ab.y)}
            </Label>
          </>
        ) : null}
        <Arrow from={a} to={b} color="var(--accent)" width={3} />
        {(() => {
          const p = beside(a, b, 16, ab.x * ab.y >= 0 ? 1 : -1);
          return ab.x !== 0 || ab.y !== 0 ? (
            <Label x={p.x} y={p.y} color="var(--accent)" arrow>
              AB
            </Label>
          ) : null;
        })()}
        {dot(a, "a", "var(--ink)", "A")}
        {dot(b, "b", "var(--accent)", "B")}
        <Label x={la.x} y={la.y} color="var(--ink)">
          A
        </Label>
        <Label x={lb.x} y={lb.y} color="var(--accent)">
          B
        </Label>
      </>
    );
  } else if (m === "sum") {
    const s: Pt = { x: a.x + b.x, y: a.y + b.y };
    info = (
      <>
        <p>
          <Vec>u</Vec> = <Col x={a.x} y={a.y} />, <Vec>v</Vec> = <Col x={b.x} y={b.y} />
        </p>
        <p className="font-semibold">
          <Vec>u</Vec> + <Vec>v</Vec> = <Col x={a.x} y={a.y} /> + <Col x={b.x} y={b.y} /> = <Col x={s.x} y={s.y} />
        </p>
      </>
    );
    const lu = beside(origin, a, 14, 1);
    const lv = beside(origin, b, 14, -1);
    const ls = beside(origin, s, 16, -1);
    content = (
      <>
        <Arrow from={a} to={s} color="var(--muted)" dashed width={1.8} />
        <Arrow from={b} to={s} color="var(--muted)" dashed width={1.8} />
        <Arrow from={origin} to={a} color="var(--accent)" />
        <Arrow from={origin} to={b} color="var(--warning)" />
        <Arrow from={origin} to={s} color="var(--success)" width={3} />
        {a.x !== 0 || a.y !== 0 ? (
          <Label x={lu.x} y={lu.y} color="var(--accent)" arrow>
            u
          </Label>
        ) : null}
        {b.x !== 0 || b.y !== 0 ? (
          <Label x={lv.x} y={lv.y} color="var(--warning)" arrow>
            v
          </Label>
        ) : null}
        {s.x !== 0 || s.y !== 0 ? (
          <Label x={ls.x} y={ls.y} color="var(--success)" arrow size={14}>
            u+v
          </Label>
        ) : null}
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
          <Vec>e₁</Vec> = <Col x={1} y={1} />, <Vec>e₂</Vec> = <Col x={1} y={-1} />, <Vec>w</Vec> = <Col x={b.x} y={b.y} />
        </p>
        <p className="font-semibold">
          {t("visual.coordinates")}: ({rational.toString(p)}, {rational.toString(q)})
        </p>
      </>
    );
    const mid: Pt = { x: Number(p.num) / Number(p.den), y: Number(p.num) / Number(p.den) };
    const l1 = beside(origin, e1, 14, 1);
    const l2 = beside(origin, e2, 14, 1);
    content = (
      <>
        <Arrow from={origin} to={mid} color="var(--accent)" dashed width={1.8} />
        <Arrow from={mid} to={b} color="var(--warning)" dashed width={1.8} />
        <Arrow from={origin} to={e1} color="var(--accent)" />
        <Arrow from={origin} to={e2} color="var(--warning)" />
        <Arrow from={origin} to={b} color="var(--success)" width={3} />
        <Label x={l1.x} y={l1.y} color="var(--accent)" arrow>
          e₁
        </Label>
        <Label x={l2.x} y={l2.y} color="var(--warning)" arrow>
          e₂
        </Label>
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
        <Axes />
        {content}
      </svg>
      <div aria-live="polite" className="text-center text-[1.05rem] leading-9 tabular-nums">
        {info}
      </div>
      <p className="text-center text-sm text-muted">{t("visual.dragHint")}</p>
    </div>
  );
}
