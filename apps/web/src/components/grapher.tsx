"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { Button, Card } from "@allmaths/ui";
import { classify, drawable, evalConstant, parameterNames, sampleCurve3, sampleSurface, specialPoints, type GraphItem, type Params, type Pt3, type View } from "@allmaths/core";
import { t } from "@/i18n";

const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#be185d", "#4d7c0f"];

interface Row {
  id: number;
  text: string;
  color: string;
  visible: boolean;
}

function cssVar(el: HTMLElement, name: string, fallback: string): string {
  const v = getComputedStyle(el).getPropertyValue(name).trim();
  return v || fallback;
}

/** A tick step of 1, 2 or 5 times a power of ten so that the labels are about `target` pixels apart. */
function niceStep(unitsPerTarget: number): number {
  const p = Math.pow(10, Math.floor(Math.log10(unitsPerTarget)));
  const m = unitsPerTarget / p;
  return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
}

const fmt = (v: number): string => String(parseFloat(v.toPrecision(6)));

function useCanvasSize(ref: React.RefObject<HTMLCanvasElement | null>): { w: number; h: number } {
  const [size, setSize] = useState({ w: 640, h: 440 });
  useEffect(() => {
    const el = ref.current?.parentElement;
    if (!el) return;
    const ro = new ResizeObserver(() => setSize({ w: Math.max(240, Math.floor(el.clientWidth)), h: Math.max(280, Math.min(560, Math.floor(el.clientWidth * 0.68))) }));
    ro.observe(el);
    return () => ro.disconnect();
  }, [ref]);
  return size;
}

// ------------------------------------------------------------------------------------------------------------- 2D
interface View2 {
  cx: number;
  cy: number;
  scale: number;
}

function Graph2D() {
  const uid = useId();
  const canvas = useRef<HTMLCanvasElement>(null);
  const { w, h } = useCanvasSize(canvas);
  const [rows, setRows] = useState<Row[]>([
    { id: 1, text: "y = sin(x)", color: COLORS[0]!, visible: true },
    { id: 2, text: "y = a*x^2 - 2", color: COLORS[1]!, visible: true },
  ]);
  const [view, setView] = useState<View2>({ cx: 0, cy: 0, scale: 50 });
  const [params, setParams] = useState<Params>({});
  const [cursor, setCursor] = useState<[number, number] | null>(null);
  const nextId = useRef(3);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const lastPinch = useRef<number | null>(null);

  const items: GraphItem[] = useMemo(() => rows.map((r) => (r.visible ? classify(r.text) : { kind: "empty" as const })), [rows]);
  const names = useMemo(() => parameterNames(items), [items]);
  const values: Params = useMemo(() => Object.fromEntries(names.map((n) => [n, params[n] ?? 1])), [names, params]);
  const range: View = useMemo(
    () => ({ xmin: view.cx - w / 2 / view.scale, xmax: view.cx + w / 2 / view.scale, ymin: view.cy - h / 2 / view.scale, ymax: view.cy + h / 2 / view.scale }),
    [view, w, h],
  );
  const drawn = useMemo(() => items.map((it) => drawable(it, values, range)), [items, values, range]);
  const special = useMemo(() => specialPoints(items, values, range), [items, values, range]);
  const [shared, setShared] = useState<"copied" | "failed" | null>(null);

  // a link made by "Copy link" carries the expressions in its #g=... part
  useEffect(() => {
    try {
      const m = /^#g=(.+)$/.exec(window.location.hash);
      if (!m) return;
      const list: unknown = JSON.parse(decodeURIComponent(escape(atob(m[1]!.replace(/-/g, "+").replace(/_/g, "/")))));
      if (!Array.isArray(list)) return;
      const texts = list.filter((x): x is string => typeof x === "string").slice(0, 8);
      if (texts.length === 0) return;
      setRows(texts.map((text, i) => ({ id: i + 1, text: text.slice(0, 200), color: COLORS[i % COLORS.length]!, visible: true })));
      nextId.current = texts.length + 1;
    } catch {
      /* a damaged link keeps the starting expressions */
    }
  }, []);

  async function copyLink() {
    try {
      const json = JSON.stringify(rows.filter((r) => r.text.trim() !== "").map((r) => r.text));
      const code = btoa(unescape(encodeURIComponent(json))).replace(/\+/g, "-").replace(/\//g, "_");
      const url = `${window.location.origin}${window.location.pathname}#g=${code}`;
      await navigator.clipboard.writeText(url);
      setShared("copied");
    } catch {
      setShared("failed");
    }
  }

  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const dpr = window.devicePixelRatio || 1;
    c.width = Math.floor(w * dpr);
    c.height = Math.floor(h * dpr);
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const bg = cssVar(c, "--surface", "#ffffff");
    const line = cssVar(c, "--line", "#d4d4d8");
    const ink = cssVar(c, "--ink", "#111111");
    const muted = cssVar(c, "--muted", "#555555");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);
    const X = (x: number) => w / 2 + (x - view.cx) * view.scale;
    const Y = (y: number) => h / 2 - (y - view.cy) * view.scale;
    // grid and tick labels
    const step = niceStep(70 / view.scale);
    ctx.font = "12px system-ui, sans-serif";
    ctx.lineWidth = 1;
    for (let gx = Math.ceil(range.xmin / step) * step; gx <= range.xmax; gx += step) {
      ctx.strokeStyle = Math.abs(gx) < step / 2 ? ink : line;
      ctx.globalAlpha = Math.abs(gx) < step / 2 ? 0.9 : 0.6;
      ctx.beginPath();
      ctx.moveTo(X(gx), 0);
      ctx.lineTo(X(gx), h);
      ctx.stroke();
      ctx.globalAlpha = 1;
      if (Math.abs(gx) > step / 2) {
        ctx.fillStyle = muted;
        ctx.textAlign = "center";
        ctx.fillText(fmt(gx), X(gx), Math.min(h - 4, Math.max(14, Y(0) + 14)));
      }
    }
    for (let gy = Math.ceil(range.ymin / step) * step; gy <= range.ymax; gy += step) {
      ctx.strokeStyle = Math.abs(gy) < step / 2 ? ink : line;
      ctx.globalAlpha = Math.abs(gy) < step / 2 ? 0.9 : 0.6;
      ctx.beginPath();
      ctx.moveTo(0, Y(gy));
      ctx.lineTo(w, Y(gy));
      ctx.stroke();
      ctx.globalAlpha = 1;
      if (Math.abs(gy) > step / 2) {
        ctx.fillStyle = muted;
        ctx.textAlign = "left";
        ctx.fillText(fmt(gy), Math.min(w - 36, Math.max(4, X(0) + 5)), Y(gy) - 3);
      }
    }
    // inequalities: shade the points that satisfy them
    drawn.forEach((d, i) => {
      if (d.kind !== "region") return;
      ctx.fillStyle = rows[i]!.color;
      ctx.globalAlpha = 0.2;
      const cell = 4;
      for (let py = 0; py < h; py += cell) {
        for (let px = 0; px < w; px += cell) {
          if (d.inside(view.cx + (px + cell / 2 - w / 2) / view.scale, view.cy - (py + cell / 2 - h / 2) / view.scale)) ctx.fillRect(px, py, cell, cell);
        }
      }
      ctx.globalAlpha = 1;
    });
    // the curves
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    drawn.forEach((d, i) => {
      const color = rows[i]!.color;
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 2.5;
      if (d.kind === "lines") {
        for (const piece of d.pieces) {
          ctx.beginPath();
          piece.forEach(([x, y], k) => (k === 0 ? ctx.moveTo(X(x), Y(y)) : ctx.lineTo(X(x), Y(y))));
          ctx.stroke();
        }
      } else if (d.kind === "segments") {
        ctx.beginPath();
        for (const [a, b, c2, e] of d.segments) {
          ctx.moveTo(X(a), Y(b));
          ctx.lineTo(X(c2), Y(e));
        }
        ctx.stroke();
      } else if (d.kind === "region") {
        ctx.setLineDash(d.strict ? [7, 6] : []);
        ctx.beginPath();
        for (const [a, b, c2, e] of d.boundary) {
          ctx.moveTo(X(a), Y(b));
          ctx.lineTo(X(c2), Y(e));
        }
        ctx.stroke();
        ctx.setLineDash([]);
      } else if (d.kind === "point") {
        ctx.beginPath();
        ctx.arc(X(d.at[0]), Y(d.at[1]), 5, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = ink;
        ctx.textAlign = "left";
        ctx.fillText(`(${fmt(d.at[0])}, ${fmt(d.at[1])})`, X(d.at[0]) + 8, Y(d.at[1]) - 8);
      }
    });
    // roots and intersections
    ctx.lineWidth = 2;
    for (const sp of special) {
      ctx.strokeStyle = ink;
      ctx.fillStyle = bg;
      ctx.beginPath();
      ctx.arc(X(sp.at[0]), Y(sp.at[1]), 5, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    }
  }, [drawn, rows, view, w, h, range, special]);

  const toWorld = useCallback(
    (px: number, py: number): [number, number] => [view.cx + (px - w / 2) / view.scale, view.cy - (py - h / 2) / view.scale],
    [view, w, h],
  );

  function zoomAt(px: number, py: number, factor: number) {
    setView((v) => {
      const scale = Math.min(5000, Math.max(2, v.scale * factor));
      const wx = v.cx + (px - w / 2) / v.scale;
      const wy = v.cy - (py - h / 2) / v.scale;
      return { scale, cx: wx - (px - w / 2) / scale, cy: wy + (py - h / 2) / scale };
    });
  }

  function onPointerDown(e: React.PointerEvent<HTMLCanvasElement>) {
    (e.target as HTMLCanvasElement).setPointerCapture(e.pointerId);
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    lastPinch.current = null;
  }
  function onPointerMove(e: React.PointerEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    setCursor(toWorld(e.clientX - rect.left, e.clientY - rect.top));
    const p = pointers.current.get(e.pointerId);
    if (!p) return;
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()] as [{ x: number; y: number }, { x: number; y: number }];
      pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
      const [a2, b2] = [...pointers.current.values()] as [{ x: number; y: number }, { x: number; y: number }];
      const d1 = Math.hypot(a.x - b.x, a.y - b.y);
      const d2 = Math.hypot(a2.x - b2.x, a2.y - b2.y);
      if (d1 > 0 && lastPinch.current !== null) zoomAt((a2.x + b2.x) / 2 - rect.left, (a2.y + b2.y) / 2 - rect.top, d2 / d1);
      lastPinch.current = d2;
      return;
    }
    const dx = e.clientX - p.x;
    const dy = e.clientY - p.y;
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    setView((v) => ({ ...v, cx: v.cx - dx / v.scale, cy: v.cy + dy / v.scale }));
  }
  function onPointerUp(e: React.PointerEvent<HTMLCanvasElement>) {
    pointers.current.delete(e.pointerId);
    lastPinch.current = null;
  }
  function onKey(e: React.KeyboardEvent<HTMLCanvasElement>) {
    const move = 60 / view.scale;
    if (e.key === "ArrowLeft") setView((v) => ({ ...v, cx: v.cx - move }));
    else if (e.key === "ArrowRight") setView((v) => ({ ...v, cx: v.cx + move }));
    else if (e.key === "ArrowUp") setView((v) => ({ ...v, cy: v.cy + move }));
    else if (e.key === "ArrowDown") setView((v) => ({ ...v, cy: v.cy - move }));
    else if (e.key === "+" || e.key === "=") zoomAt(w / 2, h / 2, 1.25);
    else if (e.key === "-") zoomAt(w / 2, h / 2, 0.8);
    else if (e.key === "Home") setView({ cx: 0, cy: 0, scale: 50 });
    else return;
    e.preventDefault();
  }
  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = c.getBoundingClientRect();
      zoomAt(e.clientX - rect.left, e.clientY - rect.top, e.deltaY < 0 ? 1.15 : 1 / 1.15);
    };
    c.addEventListener("wheel", wheel, { passive: false });
    return () => c.removeEventListener("wheel", wheel);
  });

  function setRow(id: number, patch: Partial<Row>) {
    setRows((rs) => rs.map((r) => (r.id === id ? { ...r, ...patch } : r)));
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[20rem_minmax(0,1fr)]">
      <Card className="grid content-start gap-3">
        <h2 className="text-lg font-bold">{t("grapher.expressions")}</h2>
        <ul className="grid gap-2">
          {rows.map((r, i) => {
            const d = drawn[i];
            return (
              <li key={r.id} className="grid gap-1">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={r.visible}
                    onChange={(e) => setRow(r.id, { visible: e.target.checked })}
                    aria-label={t("grapher.show", { n: i + 1 })}
                    className="size-5 shrink-0"
                    style={{ accentColor: r.color }}
                  />
                  <input
                    value={r.text}
                    onChange={(e) => setRow(r.id, { text: e.target.value })}
                    aria-label={t("grapher.expression", { n: i + 1 })}
                    maxLength={200}
                    spellCheck={false}
                    autoComplete="off"
                    autoCapitalize="off"
                    placeholder="y = x^2"
                    className="min-h-11 min-w-0 flex-1 rounded-[var(--radius-sm)] border-2 bg-bg px-3 font-mono"
                    style={{ borderColor: r.color }}
                  />
                  <button type="button" onClick={() => setRows((rs) => rs.filter((x) => x.id !== r.id))} aria-label={t("grapher.remove", { n: i + 1 })} className="size-9 shrink-0 rounded-full text-lg text-muted hover:bg-surface-2">
                    ×
                  </button>
                </div>
                {d?.kind === "error" ? (
                  <p role="alert" className="pl-7 text-sm text-danger">
                    {d.message}
                  </p>
                ) : null}
              </li>
            );
          })}
        </ul>
        {rows.length < 8 ? (
          <Button
            variant="secondary"
            onClick={() => {
              setRows((rs) => [...rs, { id: nextId.current, text: "", color: COLORS[rs.length % COLORS.length]!, visible: true }]);
              nextId.current += 1;
            }}
          >
            {t("grapher.add")}
          </Button>
        ) : null}

        {names.length > 0 ? (
          <div className="grid gap-3 border-t border-line pt-3">
            <h3 className="font-bold">{t("grapher.sliders")}</h3>
            {names.map((n) => (
              <div key={n} className="grid grid-cols-[2rem_minmax(0,1fr)_3.5rem] items-center gap-2">
                <label htmlFor={`${uid}-${n}`} className="font-mono font-bold">
                  {n}
                </label>
                <input id={`${uid}-${n}`} type="range" min={-10} max={10} step={0.1} value={values[n] ?? 1} onChange={(e) => setParams((p) => ({ ...p, [n]: Number(e.target.value) }))} className="w-full" />
                <output htmlFor={`${uid}-${n}`} className="text-right font-mono text-sm tabular-nums">
                  {fmt(values[n] ?? 1)}
                </output>
              </div>
            ))}
          </div>
        ) : null}

        <details className="border-t border-line pt-3 text-sm">
          <summary className="cursor-pointer font-semibold text-accent">{t("grapher.help")}</summary>
          <ul className="mt-2 grid gap-1 text-muted">
            <li><code>y = x^2 - 3</code>, <code>sin(x)/x</code></li>
            <li><code>x = y^2</code> · <code>x^2 + y^2 = 9</code></li>
            <li><code>r = 1 + cos(theta)</code></li>
            <li><code>(cos(t), sin(t))</code>, <code>(t, t^2), t in [0, 3]</code></li>
            <li><code>(2, 3)</code> — {t("grapher.helpPoint")}</li>
            <li><code>y &gt; x^2</code> · <code>x^2 + y^2 &lt;= 4</code> — {t("grapher.helpRegion")}</li>
            <li>{t("grapher.helpSliders")}</li>
          </ul>
        </details>
      </Card>

      <div className="min-w-0">
        <div className="relative overflow-hidden rounded-[var(--radius)] border border-line">
          <canvas
            ref={canvas}
            role="img"
            aria-label={t("grapher.canvasLabel")}
            tabIndex={0}
            style={{ width: w, height: h, touchAction: "none", cursor: "grab" }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={onPointerUp}
            onPointerLeave={() => setCursor(null)}
            onKeyDown={onKey}
            className="block bg-surface outline-offset-2"
          />
          {cursor ? (
            <p className="pointer-events-none absolute right-2 top-2 rounded bg-bg/90 px-2 py-1 font-mono text-xs tabular-nums">
              ({fmt(cursor[0])}, {fmt(cursor[1])})
            </p>
          ) : null}
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Button variant="secondary" onClick={() => zoomAt(w / 2, h / 2, 1.25)} aria-label={t("grapher.zoomIn")}>
            +
          </Button>
          <Button variant="secondary" onClick={() => zoomAt(w / 2, h / 2, 0.8)} aria-label={t("grapher.zoomOut")}>
            −
          </Button>
          <Button variant="secondary" onClick={() => setView({ cx: 0, cy: 0, scale: 50 })}>
            {t("grapher.reset")}
          </Button>
          <Button variant="secondary" onClick={copyLink}>
            {t("grapher.copyLink")}
          </Button>
          {shared ? (
            <p role="status" className="text-sm font-medium">
              {shared === "copied" ? t("grapher.linkCopied") : t("grapher.linkFailed")}
            </p>
          ) : null}
          <p className="text-sm text-muted">{t("grapher.controls2d")}</p>
        </div>
        {special.length > 0 ? (
          <Card className="mt-3">
            <h3 className="font-bold">{t("grapher.special")}</h3>
            <p className="text-sm text-muted">{t("grapher.specialNote")}</p>
            <ul className="mt-2 grid gap-1 font-mono text-sm tabular-nums">
              {special.map((sp, k) => (
                <li key={k}>
                  {sp.kind === "root" ? t("grapher.root", { n: sp.lines[0] ?? 0 }) : t("grapher.meet", { a: sp.lines[0] ?? 0, b: sp.lines[1] ?? 0 })}: ({fmt(Math.round(sp.at[0] * 1e4) / 1e4)}, {fmt(Math.round(sp.at[1] * 1e4) / 1e4)})
                </li>
              ))}
            </ul>
          </Card>
        ) : null}
      </div>
    </div>
  );
}

// ------------------------------------------------------------------------------------------------------------- 3D
function Graph3D() {
  const uid = useId();
  const canvas = useRef<HTMLCanvasElement>(null);
  const { w, h } = useCanvasSize(canvas);
  const [surface, setSurface] = useState("z = sin(x)*cos(y)");
  const [curve, setCurve] = useState("");
  const [extent, setExtent] = useState(4);
  const [wire, setWire] = useState(false);
  const [params, setParams] = useState<Params>({});
  const [angles, setAngles] = useState({ yaw: 0.7, pitch: 0.55, zoom: 1 });
  const drag = useRef<{ x: number; y: number } | null>(null);

  const surfaceExpr = surface.replace(/^\s*z\s*=\s*/i, "");
  const surfItem = useMemo(() => classify(surfaceExpr === "" ? "" : `y = ${surfaceExpr}`), [surfaceExpr]);
  const names = useMemo(() => parameterNames([classify(`y = ${surfaceExpr}`)]), [surfaceExpr]);
  const values: Params = useMemo(() => Object.fromEntries(names.map((n) => [n, params[n] ?? 1])), [names, params]);

  const mesh = useMemo(() => {
    if (surfaceExpr.trim() === "") return { grid: null as (Pt3 | null)[][] | null, error: null as string | null };
    try {
      return { grid: sampleSurface(surfaceExpr, values, [-extent, extent], [-extent, extent], 36), error: null };
    } catch (e) {
      return { grid: null, error: e instanceof Error ? e.message : "?" };
    }
  }, [surfaceExpr, values, extent]);
  const curvePts = useMemo(() => {
    const m = /^\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)\s*(?:,\s*t\s*in\s*\[\s*(.+?)\s*,\s*(.+?)\s*\])?$/.exec(curve.trim());
    if (!m) return { pts: [] as Pt3[], error: curve.trim() === "" ? null : t("grapher.curve3dHelp") };
    try {
      const t0 = m[4] !== undefined ? evalConstant(m[4], values) : 0;
      const t1 = m[5] !== undefined ? evalConstant(m[5], values) : 2 * Math.PI;
      return { pts: sampleCurve3(m[1]!, m[2]!, m[3]!, values, t0, t1), error: null };
    } catch (e) {
      return { pts: [] as Pt3[], error: e instanceof Error ? e.message : "?" };
    }
  }, [curve, values]);

  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const dpr = window.devicePixelRatio || 1;
    c.width = Math.floor(w * dpr);
    c.height = Math.floor(h * dpr);
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = cssVar(c, "--surface", "#ffffff");
    ctx.fillRect(0, 0, w, h);
    const ink = cssVar(c, "--ink", "#111");
    const R = extent;
    // scale z so the surface fits in the box
    let zmax = 0;
    for (const row of mesh.grid ?? []) for (const p of row) if (p) zmax = Math.max(zmax, Math.abs(p[2]));
    const zs = zmax > 2 * R ? (2 * R) / zmax : 1;
    const cy = Math.cos(angles.yaw);
    const sy = Math.sin(angles.yaw);
    const ce = Math.cos(angles.pitch);
    const se = Math.sin(angles.pitch);
    const unit = (Math.min(w, h) / (R * 4.2)) * angles.zoom;
    const proj = (p: Pt3): { x: number; y: number; d: number } => {
      const X = p[0] * cy - p[1] * sy;
      const Y = p[0] * sy + p[1] * cy;
      const Z = p[2] * zs;
      const Y2 = Y * ce - Z * se;
      const Z2 = Y * se + Z * ce;
      return { x: w / 2 + X * unit, y: h / 2 - Z2 * unit, d: Y2 };
    };
    // axes
    ctx.lineWidth = 1.5;
    ctx.font = "13px system-ui, sans-serif";
    ctx.fillStyle = ink;
    for (const [axis, label] of [[[R * 1.1, 0, 0], "x"], [[0, R * 1.1, 0], "y"], [[0, 0, R * 1.1 / zs], "z"]] as [Pt3, string][]) {
      const a = proj([0, 0, 0]);
      const b = proj(axis);
      ctx.strokeStyle = ink;
      ctx.globalAlpha = 0.7;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.fillText(label, b.x + 4, b.y - 4);
    }
    const grid = mesh.grid;
    if (grid) {
      const quads: { pts: { x: number; y: number }[]; d: number; z: number; shade: number }[] = [];
      for (let j = 0; j < grid.length - 1; j++) {
        for (let i = 0; i < grid[j]!.length - 1; i++) {
          const p = [grid[j]![i], grid[j]![i + 1], grid[j + 1]![i + 1], grid[j + 1]![i]];
          if (p.some((v) => v === null)) continue;
          const q = (p as Pt3[]).map(proj);
          const z = (p as Pt3[]).reduce((a, v) => a + v[2], 0) / 4;
          const u = [(p as Pt3[])[1]![0] - (p as Pt3[])[0]![0], (p as Pt3[])[1]![1] - (p as Pt3[])[0]![1], ((p as Pt3[])[1]![2] - (p as Pt3[])[0]![2]) * zs];
          const v = [(p as Pt3[])[3]![0] - (p as Pt3[])[0]![0], (p as Pt3[])[3]![1] - (p as Pt3[])[0]![1], ((p as Pt3[])[3]![2] - (p as Pt3[])[0]![2]) * zs];
          const nx = u[1]! * v[2]! - u[2]! * v[1]!;
          const ny = u[2]! * v[0]! - u[0]! * v[2]!;
          const nz = u[0]! * v[1]! - u[1]! * v[0]!;
          const len = Math.hypot(nx, ny, nz) || 1;
          const shade = 0.55 + 0.45 * Math.abs((nx * 0.3 + ny * -0.4 + nz * 0.85) / len);
          quads.push({ pts: q, d: q.reduce((a, s) => a + s.d, 0) / 4, z, shade });
        }
      }
      quads.sort((a, b) => b.d - a.d);
      const lo = -zmax || -1;
      for (const qd of quads) {
        const tNorm = zmax === 0 ? 0.5 : (qd.z - lo) / (2 * zmax);
        const hue = 240 - 240 * Math.min(1, Math.max(0, tNorm));
        ctx.beginPath();
        qd.pts.forEach((s, k) => (k === 0 ? ctx.moveTo(s.x, s.y) : ctx.lineTo(s.x, s.y)));
        ctx.closePath();
        if (!wire) {
          ctx.fillStyle = `hsl(${hue} 70% ${Math.round(38 + qd.shade * 24)}%)`;
          ctx.fill();
        }
        ctx.strokeStyle = wire ? `hsl(${hue} 70% 40%)` : "rgba(0,0,0,0.15)";
        ctx.lineWidth = wire ? 1.2 : 0.5;
        ctx.stroke();
      }
    }
    if (curvePts.pts.length > 1) {
      ctx.strokeStyle = "#dc2626";
      ctx.lineWidth = 3;
      ctx.beginPath();
      curvePts.pts.forEach((p, k) => {
        const s = proj(p);
        if (k === 0) ctx.moveTo(s.x, s.y);
        else ctx.lineTo(s.x, s.y);
      });
      ctx.stroke();
    }
  }, [mesh, curvePts, angles, extent, wire, w, h]);

  return (
    <div className="grid gap-4 lg:grid-cols-[20rem_minmax(0,1fr)]">
      <Card className="grid content-start gap-3">
        <h2 className="text-lg font-bold">{t("grapher.surface")}</h2>
        <input
          value={surface}
          onChange={(e) => setSurface(e.target.value)}
          aria-label={t("grapher.surface")}
          maxLength={200}
          spellCheck={false}
          autoComplete="off"
          placeholder="z = x^2 - y^2"
          className="min-h-11 rounded-[var(--radius-sm)] border-2 border-accent bg-bg px-3 font-mono"
        />
        {surfItem.kind === "error" || mesh.error ? (
          <p role="alert" className="text-sm text-danger">
            {mesh.error ?? (surfItem.kind === "error" ? surfItem.message : "")}
          </p>
        ) : null}
        <h2 className="mt-2 text-lg font-bold">{t("grapher.curve3d")}</h2>
        <input
          value={curve}
          onChange={(e) => setCurve(e.target.value)}
          aria-label={t("grapher.curve3d")}
          maxLength={200}
          spellCheck={false}
          autoComplete="off"
          placeholder="(cos(t), sin(t), t/3), t in [0, 12]"
          className="min-h-11 rounded-[var(--radius-sm)] border-2 border-danger bg-bg px-3 font-mono"
        />
        {curvePts.error ? (
          <p role="alert" className="text-sm text-danger">
            {curvePts.error}
          </p>
        ) : null}
        <div className="grid gap-2 border-t border-line pt-3">
          <label htmlFor={`${uid}-extent`} className="font-semibold">
            {t("grapher.extent", { n: extent })}
          </label>
          <input id={`${uid}-extent`} type="range" min={1} max={10} step={1} value={extent} onChange={(e) => setExtent(Number(e.target.value))} />
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={wire} onChange={(e) => setWire(e.target.checked)} className="size-5" />
            {t("grapher.wireframe")}
          </label>
        </div>
        {names.length > 0 ? (
          <div className="grid gap-3 border-t border-line pt-3">
            <h3 className="font-bold">{t("grapher.sliders")}</h3>
            {names.map((n) => (
              <div key={n} className="grid grid-cols-[2rem_minmax(0,1fr)_3.5rem] items-center gap-2">
                <label htmlFor={`${uid}-${n}`} className="font-mono font-bold">
                  {n}
                </label>
                <input id={`${uid}-${n}`} type="range" min={-10} max={10} step={0.1} value={values[n] ?? 1} onChange={(e) => setParams((p) => ({ ...p, [n]: Number(e.target.value) }))} />
                <output htmlFor={`${uid}-${n}`} className="text-right font-mono text-sm tabular-nums">
                  {fmt(values[n] ?? 1)}
                </output>
              </div>
            ))}
          </div>
        ) : null}
      </Card>

      <div className="min-w-0">
        <div className="overflow-hidden rounded-[var(--radius)] border border-line">
          <canvas
            ref={canvas}
            role="img"
            aria-label={t("grapher.canvasLabel3d")}
            tabIndex={0}
            style={{ width: w, height: h, touchAction: "none", cursor: "grab" }}
            onPointerDown={(e) => {
              (e.target as HTMLCanvasElement).setPointerCapture(e.pointerId);
              drag.current = { x: e.clientX, y: e.clientY };
            }}
            onPointerMove={(e) => {
              const d = drag.current;
              if (!d) return;
              const dx = e.clientX - d.x;
              const dy = e.clientY - d.y;
              drag.current = { x: e.clientX, y: e.clientY };
              setAngles((a) => ({ ...a, yaw: a.yaw + dx * 0.01, pitch: Math.min(1.5, Math.max(-0.2, a.pitch + dy * 0.01)) }));
            }}
            onPointerUp={() => (drag.current = null)}
            onPointerCancel={() => (drag.current = null)}
            onKeyDown={(e) => {
              const k = e.key;
              if (k === "ArrowLeft") setAngles((a) => ({ ...a, yaw: a.yaw - 0.1 }));
              else if (k === "ArrowRight") setAngles((a) => ({ ...a, yaw: a.yaw + 0.1 }));
              else if (k === "ArrowUp") setAngles((a) => ({ ...a, pitch: Math.min(1.5, a.pitch + 0.08) }));
              else if (k === "ArrowDown") setAngles((a) => ({ ...a, pitch: Math.max(-0.2, a.pitch - 0.08) }));
              else if (k === "+" || k === "=") setAngles((a) => ({ ...a, zoom: Math.min(4, a.zoom * 1.15) }));
              else if (k === "-") setAngles((a) => ({ ...a, zoom: Math.max(0.3, a.zoom / 1.15) }));
              else return;
              e.preventDefault();
            }}
            onWheel={(e) => setAngles((a) => ({ ...a, zoom: Math.min(4, Math.max(0.3, a.zoom * (e.deltaY < 0 ? 1.1 : 1 / 1.1))) }))}
            className="block bg-surface outline-offset-2"
          />
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Button variant="secondary" onClick={() => setAngles({ yaw: 0.7, pitch: 0.55, zoom: 1 })}>
            {t("grapher.reset")}
          </Button>
          <p className="text-sm text-muted">{t("grapher.controls3d")}</p>
        </div>
      </div>
    </div>
  );
}

export function Grapher() {
  const [tab, setTab] = useState<"2d" | "3d">("2d");
  return (
    <div>
      <div role="tablist" aria-label={t("grapher.title")} className="mb-4 flex gap-2">
        {(["2d", "3d"] as const).map((k) => (
          <button
            key={k}
            role="tab"
            type="button"
            aria-selected={tab === k}
            onClick={() => setTab(k)}
            className={`min-h-11 rounded-[var(--radius-sm)] border px-4 font-semibold ${tab === k ? "border-accent bg-accent-soft text-accent" : "border-line bg-surface hover:bg-surface-2"}`}
          >
            {t(k === "2d" ? "grapher.tab2d" : "grapher.tab3d")}
          </button>
        ))}
      </div>
      {tab === "2d" ? <Graph2D /> : <Graph3D />}
    </div>
  );
}
