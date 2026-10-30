"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { Button, Card } from "@allmaths/ui";
import { classify, drawable, evalConstant, measure, measureCircle, measurePolygon, namedPoints, parameterNames, parseParamSurface, pointAtPlace, rejectDuplicatePoints, sampleCurve3, sampleParamSurface, sampleSurface, specialPoints, type GraphItem, type Params, type Pt, type Pt3, type View } from "@allmaths/core";
import { t } from "@/i18n";
import { RichInline } from "./lesson/rich";
import type { ExactPointDto } from "@/app/api/graph/exact/route";

type Tool = "move" | "point" | "segment" | "line" | "circle" | "polygon";
const TOOLS: {
  tool: Tool;
  label: "toolMove" | "toolPoint" | "toolSegment" | "toolLine" | "toolCircle" | "toolPolygon";
  help: "toolHelpMove" | "toolHelpPoint" | "toolHelpSegment" | "toolHelpLine" | "toolHelpCircle" | "toolHelpPolygon";
}[] = [
  { tool: "move", label: "toolMove", help: "toolHelpMove" },
  { tool: "point", label: "toolPoint", help: "toolHelpPoint" },
  { tool: "segment", label: "toolSegment", help: "toolHelpSegment" },
  { tool: "line", label: "toolLine", help: "toolHelpLine" },
  { tool: "circle", label: "toolCircle", help: "toolHelpCircle" },
  { tool: "polygon", label: "toolPolygon", help: "toolHelpPolygon" },
];
const HELP: {
  key: "function" | "xfunction" | "curve" | "polar" | "parametric" | "parametricRange" | "point" | "segment" | "line" | "circle" | "polygon" | "slopefield" | "ode" | "inequality" | "region" | "slider";
  example: string;
}[] = [
  { key: "function", example: "y = x^2 - 3" },
  { key: "xfunction", example: "x = y^2" },
  { key: "curve", example: "x^2 + y^2 = 9" },
  { key: "polar", example: "r = 1 + cos(theta)" },
  { key: "parametric", example: "(cos(t), sin(t))" },
  { key: "parametricRange", example: "(t, t^2), t in [0, 3]" },
  { key: "point", example: "A(2, 3)" },
  { key: "segment", example: "segment(A, B)" },
  { key: "line", example: "line(A, B)" },
  { key: "circle", example: "circle(A, B)" },
  { key: "polygon", example: "polygon(A, B, C)" },
  { key: "slopefield", example: "y' = x - y" },
  { key: "ode", example: "ode(y' = x - y, A)" },
  { key: "inequality", example: "y > x^2" },
  { key: "region", example: "x^2 + y^2 <= 4" },
  { key: "slider", example: "y = a*x^2 + b" },
];
/** Ready-made surfaces of the geometry course; each one can be edited in the box after it is chosen. */
const SURFACE_PRESETS: { key: "paraboloid" | "saddle" | "sphere" | "ellipsoid" | "cylinder" | "cone" | "torus"; text: string; extent: number }[] = [
  { key: "paraboloid", text: "z = x^2 + y^2", extent: 3 },
  { key: "saddle", text: "z = x^2 - y^2", extent: 3 },
  { key: "sphere", text: "(3*sin(u)*cos(v), 3*sin(u)*sin(v), 3*cos(u)), u in [0, pi], v in [0, 2*pi]", extent: 4 },
  { key: "ellipsoid", text: "(3*sin(u)*cos(v), 2*sin(u)*sin(v), cos(u)), u in [0, pi], v in [0, 2*pi]", extent: 4 },
  { key: "cylinder", text: "(2*cos(v), 2*sin(v), u), u in [-2, 2], v in [0, 2*pi]", extent: 4 },
  { key: "cone", text: "(u*cos(v), u*sin(v), u), u in [-2, 2], v in [0, 2*pi]", extent: 3 },
  { key: "torus", text: "((3 + cos(u))*cos(v), (3 + cos(u))*sin(v), sin(u)), u in [0, 2*pi], v in [0, 2*pi]", extent: 5 },
];
const MAX_ROWS = 24;
const NUMBER = /^-?\d+(\.\d+)?$/;

/** The next free point name: A, B, C, ... then A1, B1, ... */
function pointName(used: Set<string>): string {
  for (let round = 0; round < 10; round++) {
    for (const ch of "ABCDEFGHIJKLMNOPQRSTUVWXYZ") {
      const name = round === 0 ? ch : `${ch}${round}`;
      if (!used.has(name)) return name;
    }
  }
  return "P99";
}

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
  const [tool, setTool] = useState<Tool>("move");
  const [pending, setPending] = useState<string | null>(null);
  const [polyPending, setPolyPending] = useState<string[]>([]);
  const press = useRef<{ x: number; y: number; lx: number; ly: number; moved: boolean; multi: boolean } | null>(null);
  const dragging = useRef<{ rowId: number; name: string } | null>(null);

  const typed: GraphItem[] = useMemo(() => rows.map((r) => (r.visible ? classify(r.text) : { kind: "empty" as const })), [rows]);
  const names = useMemo(() => parameterNames(typed), [typed]);
  const values: Params = useMemo(() => Object.fromEntries(names.map((n) => [n, params[n] ?? 1])), [names, params]);
  // two points cannot be in the same place or have the same name: the later row shows why, and is not drawn
  const items: GraphItem[] = useMemo(() => rejectDuplicatePoints(typed, values), [typed, values]);
  const [notice, setNotice] = useState<string | null>(null);
  const range: View = useMemo(
    () => ({ xmin: view.cx - w / 2 / view.scale, xmax: view.cx + w / 2 / view.scale, ymin: view.cy - h / 2 / view.scale, ymax: view.cy + h / 2 / view.scale }),
    [view, w, h],
  );
  const points = useMemo(() => namedPoints(items, values), [items, values]);
  // a point that was chosen for a segment, a circle or a polygon and then removed (or refused) is no longer chosen
  useEffect(() => {
    if (pending !== null && !points[pending]) setPending(null);
    if (polyPending.some((n) => !points[n])) setPolyPending((l) => l.filter((n) => points[n]));
  }, [points, pending, polyPending]);
  const drawn = useMemo(() => items.map((it) => drawable(it, values, range, points)), [items, values, range, points]);
  const special = useMemo(() => specialPoints(items, values, range), [items, values, range]);
  const measures = useMemo(() => {
    interface Entry {
      key: string;
      title: string;
      exact: boolean;
      rows: { label: string; value: string }[];
    }
    const out: Entry[] = [];
    const unit = (label: string, value: string): string => (label === "length" || label === "radius" || label === "perimeter" ? `${value} ${t("grapher.unitLength")}` : label === "area" ? `${value} ${t("grapher.unitArea")}` : value);
    items.forEach((it, i) => {
      const key = `${rows[i]!.id}`;
      if (it.kind === "segment") {
        const pa = points[it.a];
        const pb = points[it.b];
        if (!pa || !pb || (pa[0] === pb[0] && pa[1] === pb[1])) return;
        const m = measure(pa, pb);
        const list = it.mode === "segment" ? [{ label: t("grapher.length"), value: `${m.length} ${t("grapher.unitLength")}` }, { label: t("grapher.midpoint"), value: m.midpoint }] : [];
        out.push({ key, title: t(it.mode === "line" ? "grapher.measureLine" : "grapher.measureSegment", { a: it.a, b: it.b }), exact: m.exact, rows: [...list, { label: t("grapher.equation"), value: m.equation }] });
      } else if (it.kind === "circle") {
        const c = points[it.center];
        const p = points[it.through];
        if (!c || !p || (c[0] === p[0] && c[1] === p[1])) return;
        const m = measureCircle(c, p);
        out.push({ key, title: t("grapher.measureCircle", { a: it.center, b: it.through }), exact: m.exact, rows: m.lines.map((l) => ({ label: t(`grapher.m.${l.label}`), value: unit(l.label, l.value) })) });
      } else if (it.kind === "polygon") {
        const pts = it.names.map((n) => points[n]);
        if (pts.some((p) => !p)) return;
        const m = measurePolygon(pts as Pt[]);
        out.push({ key, title: t("grapher.measurePolygon", { names: it.names.join("") }), exact: m.exact, rows: m.lines.map((l) => ({ label: t(`grapher.m.${l.label}`), value: unit(l.label, l.value) })) });
      }
    });
    return out;
  }, [items, points, rows]);
  const [exact, setExact] = useState<ExactPointDto[]>([]);
  const exactCache = useRef(new Map<string, ExactPointDto[]>());

  // ask the math engine to make the numeric roots and intersections exact (it answers only when it can prove the value)
  useEffect(() => {
    if (special.length === 0) {
      setExact([]);
      return;
    }
    const lines: Record<string, string> = {};
    items.forEach((it, i) => {
      if (it.kind === "function") lines[String(i + 1)] = it.expr;
    });
    const params: Record<string, string> = {};
    for (const [n, v] of Object.entries(values)) {
      const tenths = Math.round(v * 10);
      params[n] = tenths % 10 === 0 ? String(tenths / 10) : `${tenths}/10`;
    }
    const body = JSON.stringify({ lines, params, candidates: special.map((sp) => ({ lines: sp.lines, x: sp.at[0] })) });
    const known = exactCache.current.get(body);
    if (known) {
      setExact(known);
      return;
    }
    const ctl = new AbortController();
    const timer = setTimeout(() => {
      fetch("/api/graph/exact", { method: "POST", headers: { "content-type": "application/json" }, body, signal: ctl.signal })
        .then((r) => (r.ok ? (r.json() as Promise<{ points: ExactPointDto[] }>) : { points: [] }))
        .then((d) => {
          if (exactCache.current.size > 60) exactCache.current.clear();
          exactCache.current.set(body, d.points);
          setExact(d.points);
        })
        .catch(() => undefined);
    }, 600);
    return () => {
      clearTimeout(timer);
      ctl.abort();
    };
  }, [special, items, values]);
  const exactFor = (sp: { lines: number[]; at: [number, number] }): ExactPointDto | undefined =>
    exact.find((e) => e.lines.join() === sp.lines.join() && Math.abs(e.x - sp.at[0]) < 1e-5 * Math.max(1, Math.abs(sp.at[0])));
  const [shared, setShared] = useState<"copied" | "failed" | null>(null);

  // a link made by "Copy link" carries the expressions in its #g=... part
  useEffect(() => {
    try {
      const m = /^#g=(.+)$/.exec(window.location.hash);
      if (!m) return;
      const list: unknown = JSON.parse(decodeURIComponent(escape(atob(m[1]!.replace(/-/g, "+").replace(/_/g, "/")))));
      if (!Array.isArray(list)) return;
      const texts = list.filter((x): x is string => typeof x === "string").slice(0, MAX_ROWS);
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
      } else if (d.kind === "polygon") {
        ctx.beginPath();
        d.pts.forEach(([x, y], k) => (k === 0 ? ctx.moveTo(X(x), Y(y)) : ctx.lineTo(X(x), Y(y))));
        ctx.closePath();
        ctx.globalAlpha = 0.16;
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.stroke();
      } else if (d.kind === "slopefield") {
        // short segments of the right slope on a grid, then the solution curve
        const gap = 34;
        ctx.globalAlpha = 0.55;
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        for (let px = gap / 2; px < w; px += gap) {
          for (let py = gap / 2; py < h; py += gap) {
            const wx = view.cx + (px - w / 2) / view.scale;
            const wy = view.cy - (py - h / 2) / view.scale;
            const slope = d.f(wx, wy);
            if (!Number.isFinite(slope)) continue;
            const ang = Math.atan2(-slope, 1); // screen y points down
            const half = gap * 0.36;
            ctx.moveTo(px - half * Math.cos(ang), py - half * Math.sin(ang));
            ctx.lineTo(px + half * Math.cos(ang), py + half * Math.sin(ang));
          }
        }
        ctx.stroke();
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2.8;
        for (const piece of d.curve) {
          ctx.beginPath();
          piece.forEach(([x, y], k) => (k === 0 ? ctx.moveTo(X(x), Y(y)) : ctx.lineTo(X(x), Y(y))));
          ctx.stroke();
        }
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
        const it = items[i];
        const label = it?.kind === "point" && it.name ? it.name : "";
        ctx.beginPath();
        const chosen = label !== "" && (label === pending || polyPending.includes(label));
        ctx.arc(X(d.at[0]), Y(d.at[1]), chosen ? 6 : 4, 0, 2 * Math.PI);
        ctx.fill();
        if (chosen) {
          ctx.strokeStyle = ink;
          ctx.lineWidth = 2;
          ctx.stroke();
        }
        ctx.fillStyle = ink;
        ctx.textAlign = "left";
        ctx.font = "600 13px system-ui, sans-serif";
        ctx.fillText(`${label}(${fmt(d.at[0])}, ${fmt(d.at[1])})`, X(d.at[0]) + 7, Y(d.at[1]) - 7);
        ctx.font = "12px system-ui, sans-serif";
      }
    });
    // roots and intersections
    ctx.lineWidth = 1.5;
    for (const sp of special) {
      ctx.strokeStyle = ink;
      ctx.fillStyle = bg;
      ctx.beginPath();
      ctx.arc(X(sp.at[0]), Y(sp.at[1]), 3, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    }
  }, [drawn, rows, items, pending, polyPending, view, w, h, range, special]);

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

  /** The nearest named point within reach of a touch at (px, py), with the row it comes from. */
  function pointAt(px: number, py: number): { name: string; rowId: number; movable: boolean } | null {
    let best: { name: string; rowId: number; movable: boolean; d: number } | null = null;
    items.forEach((it, i) => {
      if (it.kind !== "point" || !it.name) return;
      const at = points[it.name];
      if (!at) return;
      const d = Math.hypot(w / 2 + (at[0] - view.cx) * view.scale - px, h / 2 - (at[1] - view.cy) * view.scale - py);
      if (d <= 14 && (!best || d < best.d)) best = { name: it.name, rowId: rows[i]!.id, movable: NUMBER.test(it.x) && NUMBER.test(it.y), d };
    });
    return best;
  }

  /**
   * A position under a touch, moved to the nearest whole number so that points such as (1, 1) are easy to reach.
   * Half steps only when the view is zoomed in a lot; whole numbers (or larger round steps) when it is zoomed out.
   */
  function snapped(px: number, py: number): [number, number] {
    const unit = view.scale >= 150 ? 0.5 : view.scale >= 18 ? 1 : Math.max(1, niceStep(20 / view.scale));
    const [wx, wy] = toWorld(px, py);
    const round = (v: number) => parseFloat((Math.round(v / unit) * unit).toFixed(6));
    return [round(wx), round(wy)];
  }

  /** "A point is already at (4, -2): G. Two points cannot be in the same place." */
  function pointThere(at: [number, number], name?: string): string {
    const where = `(${fmt(at[0])}, ${fmt(at[1])})`;
    return name ? t("grapher.pointThereNamed", { at: where, name }) : t("grapher.pointThere", { at: where });
  }

  /**
   * A new named point at `at`. When a point is already there (the touch was far from it but snapped to the same coordinates) that point is
   * used instead of a second one; null when nothing can be added (the list is full, or the place holds a point without a name).
   */
  function addPoint(at: [number, number]): { name: string; existing: boolean } | null {
    const twin = pointAtPlace(items, values, at);
    if (twin?.name) return { name: twin.name, existing: true };
    if (twin) {
      setNotice(pointThere(at));
      return null;
    }
    const used = new Set(items.flatMap((it) => (it.kind === "point" && it.name ? [it.name] : [])));
    const name = pointName(used);
    return addRow(`${name} = (${at[0]}, ${at[1]})`) ? { name, existing: false } : null;
  }

  function toolClick(px: number, py: number) {
    setNotice(null);
    const hit = pointAt(px, py);
    if (tool === "point") {
      if (hit) setNotice(pointThere(points[hit.name]!, hit.name));
      else {
        const at = snapped(px, py);
        const added = addPoint(at);
        if (added?.existing) setNotice(pointThere(at, added.name));
      }
      return;
    }
    if (tool === "polygon") {
      const name = hit ? hit.name : addPoint(snapped(px, py))?.name;
      if (!name) return;
      if (polyPending.length >= 3 && name === polyPending[0]) finishPolygon();
      else if (polyPending[polyPending.length - 1] !== name && !polyPending.includes(name)) setPolyPending((l) => [...l, name]);
      return;
    }
    if (tool !== "segment" && tool !== "line" && tool !== "circle") return;
    const name = hit ? hit.name : addPoint(snapped(px, py))?.name;
    if (!name) return;
    if (pending === null) setPending(name);
    else if (pending !== name) {
      if (addRow(`${tool}(${pending}, ${name})`)) setPending(null);
    }
  }

  function finishPolygon() {
    if (polyPending.length >= 3 && !addRow(`polygon(${polyPending.join(", ")})`)) return;
    setPolyPending([]);
  }

  function onPointerDown(e: React.PointerEvent<HTMLCanvasElement>) {
    (e.target as HTMLCanvasElement).setPointerCapture(e.pointerId);
    const rect = e.currentTarget.getBoundingClientRect();
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    lastPinch.current = null;
    press.current = { x: e.clientX, y: e.clientY, lx: e.clientX - rect.left, ly: e.clientY - rect.top, moved: false, multi: pointers.current.size > 1 };
    if (tool === "move" && pointers.current.size === 1) {
      const hit = pointAt(e.clientX - rect.left, e.clientY - rect.top);
      dragging.current = hit?.movable ? { rowId: hit.rowId, name: hit.name } : null;
    }
  }
  function onPointerMove(e: React.PointerEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    setCursor(toWorld(e.clientX - rect.left, e.clientY - rect.top));
    const p = pointers.current.get(e.pointerId);
    if (!p) return;
    if (press.current && Math.hypot(e.clientX - press.current.x, e.clientY - press.current.y) > 5) press.current.moved = true;
    if (pointers.current.size === 2) {
      if (press.current) press.current.multi = true;
      const [a, b] = [...pointers.current.values()] as [{ x: number; y: number }, { x: number; y: number }];
      pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
      const [a2, b2] = [...pointers.current.values()] as [{ x: number; y: number }, { x: number; y: number }];
      const d1 = Math.hypot(a.x - b.x, a.y - b.y);
      const d2 = Math.hypot(a2.x - b2.x, a2.y - b2.y);
      if (d1 > 0 && lastPinch.current !== null) zoomAt((a2.x + b2.x) / 2 - rect.left, (a2.y + b2.y) / 2 - rect.top, d2 / d1);
      lastPinch.current = d2;
      return;
    }
    if (dragging.current) {
      const [x, y] = snapped(e.clientX - rect.left, e.clientY - rect.top);
      const { rowId, name } = dragging.current;
      // two points cannot be in the same place: the point stays where it was until it is over a free place
      const twin = pointAtPlace(items, values, [x, y], rows.findIndex((r) => r.id === rowId));
      if (twin) {
        setNotice(pointThere([x, y], twin.name));
        return;
      }
      setNotice(null);
      setRow(rowId, { text: `${name} = (${x}, ${y})` });
      return;
    }
    const dx = e.clientX - p.x;
    const dy = e.clientY - p.y;
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (tool !== "move" && !press.current?.moved) return;
    setView((v) => ({ ...v, cx: v.cx - dx / v.scale, cy: v.cy + dy / v.scale }));
  }
  function onPointerUp(e: React.PointerEvent<HTMLCanvasElement>) {
    const was = press.current;
    pointers.current.delete(e.pointerId);
    lastPinch.current = null;
    dragging.current = null;
    press.current = null;
    if (e.type === "pointerup" && was && !was.moved && !was.multi && tool !== "move") toolClick(was.lx, was.ly); // the place where the touch began (the page may have scrolled to focus the picture)
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
    else if (e.key === "Escape") {
      setPending(null);
      setPolyPending([]);
    }
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
  /** Adds a line; false (with a message) when the list already has the most lines it can hold. */
  function addRow(text: string): boolean {
    if (rows.length >= MAX_ROWS) {
      setNotice(t("grapher.full", { n: MAX_ROWS }));
      return false;
    }
    const id = nextId.current;
    nextId.current += 1;
    setRows((rs) => (rs.length >= MAX_ROWS ? rs : [...rs, { id, text, color: COLORS[rs.length % COLORS.length]!, visible: true }]));
    return true;
  }
  /** A new empty line at the end of the list; its id, or null (with a message) when the list is full. */
  function addEmptyRow(): number | null {
    if (rows.length >= MAX_ROWS) {
      setNotice(t("grapher.full", { n: MAX_ROWS }));
      return null;
    }
    const id = nextId.current;
    nextId.current += 1;
    setRows((rs) => [...rs, { id, text: "", color: COLORS[rs.length % COLORS.length]!, visible: true }]);
    return id;
  }

  // the line to put the cursor in after the lines have been drawn again
  const focusRow = useRef<number | null>(null);
  useEffect(() => {
    if (focusRow.current === null) return;
    document.getElementById(`${uid}-row-${focusRow.current}`)?.focus();
    focusRow.current = null;
  }, [rows, uid]);

  /**
   * Enter in a line goes on to the next line, so that several points can be typed one after the other: on the last line it opens a new empty
   * line (an empty last line is not repeated).
   */
  function enterOnRow(index: number) {
    const current = rows[index];
    if (!current) return;
    const next = rows[index + 1];
    if (next) {
      focusRow.current = next.id;
      document.getElementById(`${uid}-row-${next.id}`)?.focus();
      return;
    }
    if (current.text.trim() === "") return;
    const id = addEmptyRow();
    if (id !== null) focusRow.current = id;
  }

  /** An example from the help goes into the first empty line, or into a new one. */
  function fillExample(text: string) {
    const empty = rows.find((r) => r.text.trim() === "");
    if (empty) setRow(empty.id, { text });
    else addRow(text);
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
                    id={`${uid}-row-${r.id}`}
                    value={r.text}
                    onChange={(e) => setRow(r.id, { text: e.target.value })}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        enterOnRow(i);
                      }
                    }}
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
        {rows.length < MAX_ROWS ? (
          <Button
            variant="secondary"
            onClick={() => {
              const id = addEmptyRow();
              if (id !== null) focusRow.current = id;
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
          <summary className="cursor-pointer font-semibold text-accent">{t("grapher.helpTitle")}</summary>
          <p className="mt-2 text-muted">{t("grapher.helpTip")}</p>
          <dl className="mt-2 grid gap-2">
            {HELP.map((h) => (
              <div key={h.key} className="grid gap-1">
                <dt className="text-muted">{t(`grapher.ex.${h.key}`)}</dt>
                <dd>
                  <button type="button" onClick={() => fillExample(h.example)} className="rounded-[var(--radius-sm)] border border-line bg-surface-2 px-2 py-1 text-left font-mono hover:bg-accent-soft">
                    {h.example}
                  </button>
                </dd>
              </div>
            ))}
          </dl>
        </details>
      </Card>

      <div className="min-w-0">
        <div role="radiogroup" aria-label={t("grapher.tools")} className="mb-2 flex flex-wrap items-center gap-2">
          {TOOLS.map((k) => (
            <button
              key={k.tool}
              type="button"
              role="radio"
              aria-checked={tool === k.tool}
              onClick={() => {
                setTool(k.tool);
                setPending(null);
                setPolyPending([]);
                setNotice(null);
              }}
              className={`min-h-10 rounded-[var(--radius-sm)] border px-3 font-semibold ${tool === k.tool ? "border-accent bg-accent-soft text-accent" : "border-line bg-surface hover:bg-surface-2"}`}
            >
              {t(`grapher.${k.label}`)}
            </button>
          ))}
          {tool === "polygon" && polyPending.length > 0 ? (
            <>
              <p className="text-sm text-muted">{t("grapher.polygonProgress", { names: polyPending.join(", ") })}</p>
              {polyPending.length >= 3 ? (
                <Button variant="secondary" onClick={finishPolygon}>
                  {t("grapher.finishPolygon")}
                </Button>
              ) : null}
            </>
          ) : (
            <p className="text-sm text-muted">{pending ? t("grapher.pending", { name: pending }) : t(`grapher.${TOOLS.find((k) => k.tool === tool)!.help}`)}</p>
          )}
        </div>
        <div className="relative overflow-hidden rounded-[var(--radius)] border border-line">
          <canvas
            ref={canvas}
            role="img"
            aria-label={t("grapher.canvasLabel")}
            tabIndex={0}
            style={{ width: w, height: h, touchAction: "none", cursor: tool === "move" ? "grab" : "crosshair" }}
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
          {/* over the bottom of the picture, not above it: a message that pushed the picture down would move it under a drag in progress */}
          {notice ? (
            <p role="status" className="pointer-events-none absolute inset-x-2 bottom-2 rounded-[var(--radius-sm)] bg-warning-soft px-3 py-2 text-sm font-medium text-warning shadow-[var(--shadow-sm)]">
              {notice}
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
        {measures.length > 0 ? (
          <Card className="mt-3">
            <h3 className="font-bold">{t("grapher.measures")}</h3>
            <ul className="mt-2 grid gap-3 text-sm">
              {measures.map((m) => (
                <li key={m.key} className="grid gap-0.5">
                  <span className="font-semibold">{m.title}</span>
                  {m.rows.map((r) => (
                    <span key={r.label} className="font-mono tabular-nums">
                      {r.label}: {m.exact ? "" : "≈ "}
                      {r.value}
                    </span>
                  ))}
                </li>
              ))}
              {measures.some((m) => !m.exact) ? <li className="text-muted">{t("grapher.approxNote")}</li> : null}
            </ul>
          </Card>
        ) : null}
        {special.length > 0 ? (
          <Card className="mt-3">
            <h3 className="font-bold">{t("grapher.special")}</h3>
            <p className="text-sm text-muted">{t("grapher.specialNote")}</p>
            <ul className="mt-2 grid gap-1 font-mono text-sm tabular-nums">
              {special.map((sp, k) => {
                const ex = exactFor(sp);
                return (
                  <li key={k} className="flex flex-wrap items-center gap-x-2">
                    <span>{sp.kind === "root" ? t("grapher.root", { n: sp.lines[0] ?? 0 }) : t("grapher.meet", { a: sp.lines[0] ?? 0, b: sp.lines[1] ?? 0 })}:</span>
                    {ex ? (
                      <RichInline html={ex.html} />
                    ) : (
                      <span title={t("grapher.approx")}>
                        ≈ ({fmt(Math.round(sp.at[0] * 1e4) / 1e4)}, {fmt(Math.round(sp.at[1] * 1e4) / 1e4)})
                      </span>
                    )}
                  </li>
                );
              })}
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
  // a parametric surface (x(u,v), y(u,v), z(u,v)), u in [a, b], v in [c, d]: a sphere, a torus, a cone ...
  const param = useMemo(() => parseParamSurface(surface), [surface]);
  const surfItem = useMemo(() => classify(surfaceExpr === "" || param ? "" : `y = ${surfaceExpr}`), [surfaceExpr, param]);
  const names = useMemo(() => {
    const text = param ? `${param.x}+${param.y}+${param.z}+${param.u.join("+")}+${param.v.join("+")}` : surfaceExpr;
    return parameterNames([classify(`y = ${text}`)]).filter((n) => !(param && (n === "u" || n === "v")));
  }, [surfaceExpr, param]);
  const values: Params = useMemo(() => Object.fromEntries(names.map((n) => [n, params[n] ?? 1])), [names, params]);

  const mesh = useMemo(() => {
    if (surfaceExpr.trim() === "") return { grid: null as (Pt3 | null)[][] | null, error: null as string | null };
    try {
      if (param) return { grid: sampleParamSurface(param, values, (txt) => evalConstant(txt, values), 40), error: null };
      return { grid: sampleSurface(surfaceExpr, values, [-extent, extent], [-extent, extent], 36), error: null };
    } catch (e) {
      return { grid: null, error: e instanceof Error ? e.message : "?" };
    }
  }, [surfaceExpr, param, values, extent]);
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
        <div>
          <p className="text-sm text-muted">{t("grapher.presetsTip")}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {SURFACE_PRESETS.map((p) => (
              <button
                key={p.key}
                type="button"
                onClick={() => {
                  setSurface(p.text);
                  setExtent(p.extent);
                }}
                className="rounded-full border border-line bg-surface-2 px-3 py-1.5 text-sm font-semibold hover:bg-accent-soft"
              >
                {t(`grapher.preset.${p.key}`)}
              </button>
            ))}
          </div>
        </div>
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
