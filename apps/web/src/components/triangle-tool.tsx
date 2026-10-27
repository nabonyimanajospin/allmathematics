"use client";

import { useEffect, useId, useRef, useState, type FormEvent, type ReactNode } from "react";
import { LINE_FORMS, LINE_GROUPS, type Figure, type FigureItem, type LineForm, type LineGroup } from "@allmaths/core";
import { Button, Card, buttonClass, inputClass } from "@allmaths/ui";
import { t, type MessageKey } from "@/i18n";
import type { TriangleCircleDto, TriangleDto, TriangleLineDto, TriangleResponseDto } from "@/lib/triangle-types";
import { FigureExplorer } from "./lesson/figure-explorer";
import { RichInline } from "./lesson/rich";

const VERTICES = ["A", "B", "C"] as const;
const AXES = ["x", "y"] as const;

/** Examples: a right triangle, the running triangle of the lessons, the triangle of the notes, a triangle with three different radicals. */
const EXAMPLES: string[][][] = [
  [["-2", "2"], ["-2", "-1"], ["2", "2"]],
  [["0", "0"], ["14", "0"], ["5", "12"]],
  [["-3", "2"], ["1", "5"], ["5", "-7"]],
  [["0", "0"], ["4", "1"], ["1", "3"]],
];

/** The drawing: the triangle, its circles, its centers and the Euler line. A vertex that is also H is named "A=H". */
function buildFigure(d: TriangleDto): Figure {
  const p = d.figure.points;
  const same = (u: number[] | undefined, v: number[] | undefined) => !!u && !!v && Math.abs(u[0]! - v[0]!) < 1e-9 && Math.abs(u[1]! - v[1]!) < 1e-9;
  const orthoVertex = VERTICES.find((v) => same(p[v], p.H));
  const items: FigureItem[] = [
    { t: "polygon", pts: [...VERTICES], fill: "accent", color: "accent" },
    { t: "circle", center: "I", r: d.figure.incircle.r, color: "warning" },
    { t: "circle", center: "O", r: d.figure.circumcircle.r, color: "success", dashed: true },
  ];
  // the line is given by two positions, because H may be drawn as a vertex (a right triangle) and then has no point of its own
  if (d.euler && !same(p.O, p.H)) items.push({ t: "line", through: [[...p.O!], [...p.H!]], dashed: true, color: "muted", label: "Euler" });
  for (const v of VERTICES) items.push({ t: "point", id: v, at: [...p[v]!], color: "ink", label: v === orthoVertex ? `${v}=H` : v });
  items.push({ t: "point", id: "G", at: [...p.G!], color: "success" });
  items.push({ t: "point", id: "I", at: [...p.I!], color: "warning" });
  items.push({ t: "point", id: "O", at: [...p.O!], color: "success" });
  if (!orthoVertex) items.push({ t: "point", id: "H", at: [...p.H!], color: "danger" });
  return { dim: 2, alt: t("triangle.figureAlt"), view: d.figure.view, items };
}

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <Card id={id} className="grid scroll-mt-24 gap-3">
      <h2 className="text-xl font-bold">{title}</h2>
      {children}
    </Card>
  );
}

/** A label with a formula; a long formula scrolls inside its row instead of widening the page. */
function Row({ label, html }: { label: string; html: string }) {
  const cell = useRef<HTMLElement>(null);
  const [scrolls, setScrolls] = useState(false);
  // an equation stays on one line; when it is wider than its cell the cell scrolls, and then it can be reached with the keyboard
  useEffect(() => {
    const el = cell.current;
    if (!el) return;
    const measure = () => setScrolls(el.scrollWidth > el.clientWidth + 1);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [html]);
  return (
    <div className="grid gap-1 border-t border-line pt-2 sm:grid-cols-[minmax(11rem,16rem)_1fr] sm:gap-4">
      <dt className="text-sm font-semibold text-muted">{label}</dt>
      <dd ref={cell} tabIndex={scrolls ? 0 : undefined} className="min-w-0 overflow-x-auto [&_.katex-html]:whitespace-nowrap">
        <RichInline html={html} />
      </dd>
    </div>
  );
}

function CircleBlock({ name, c }: { name: string; c: TriangleCircleDto }) {
  return (
    <Card className="grid gap-2">
      <h3 className="text-lg font-bold">{name}</h3>
      <dl className="grid gap-2">
        <Row label={t("triangle.center")} html={c.centerHtml} />
        <Row label={t("triangle.radius")} html={c.radiusHtml} />
        <Row label={t("triangle.analytic")} html={c.analyticHtml} />
        <Row label={t("triangle.general")} html={c.generalHtml} />
        <Row label={t("triangle.parametric")} html={c.parametricHtml} />
        <Row label={t("triangle.circlePerimeter")} html={c.perimeterHtml} />
        <Row label={t("triangle.circleArea")} html={c.areaHtml} />
      </dl>
    </Card>
  );
}

/** One line with its length and its eight equations, all visible. */
function LineCard({ line }: { line: TriangleLineDto }) {
  const inside = line.group === "perpbisector";
  return (
    <Card className="grid gap-2">
      <h3 className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-lg font-bold">
        <span>{t(`triangle.lineNames.${line.group}` as MessageKey, { label: line.label })}</span>
        <span className="text-sm font-normal text-muted">
          {t(inside ? "triangle.lengthInside" : "triangle.length")}: <RichInline html={line.lengthHtml} />
        </span>
      </h3>
      <dl className="grid gap-2">
        <Row label={t("triangle.ends")} html={`${line.fromHtml} → ${line.toHtml}`} />
        {LINE_FORMS.map((form: LineForm) => (
          <Row key={form} label={t(`triangle.forms.${form}` as MessageKey)} html={line.forms[form] ?? `<span class="text-muted">${t("triangle.noIntercept")}</span>`} />
        ))}
      </dl>
    </Card>
  );
}

/** The fifteen lines, one kind at a time (sides, medians, altitudes, angle bisectors, perpendicular bisectors). */
function LinesSection({ d }: { d: TriangleDto }) {
  const uid = useId();
  const [group, setGroup] = useState<LineGroup>("side");
  return (
    <Section id="triangle-lines" title={t("triangle.lines")}>
      <p className="text-muted">{t("triangle.linesLead")}</p>
      <div role="tablist" aria-label={t("triangle.lines")} className="flex flex-wrap gap-2">
        {LINE_GROUPS.map((g) => (
          <button
            key={g}
            type="button"
            role="tab"
            id={`${uid}-tab-${g}`}
            aria-selected={g === group}
            aria-controls={`${uid}-panel`}
            onClick={() => setGroup(g)}
            className={buttonClass(g === group ? "primary" : "secondary")}
          >
            {t(`triangle.groups.${g}` as MessageKey)}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`${uid}-panel`} aria-labelledby={`${uid}-tab-${group}`} className="grid gap-4">
        {d.lines
          .filter((l) => l.group === group)
          .map((l) => (
            <LineCard key={l.id} line={l} />
          ))}
      </div>
    </Section>
  );
}

/** `start`: the points to begin with, and whether to analyze them at once (when the solver recognized a triangle problem). */
export function TriangleTool({ start }: { start?: { points: string[][]; run: boolean } }) {
  const uid = useId();
  const [exampleIndex, setExampleIndex] = useState(0);
  const [values, setValues] = useState<string[][]>(start?.points ?? EXAMPLES[0]!);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TriangleDto | null>(null);

  function setValue(row: number, col: number, v: string) {
    setValues((all) => all.map((r, i) => (i === row ? r.map((c, j) => (j === col ? v : c)) : r)));
  }

  function nextExample() {
    const next = (exampleIndex + 1) % EXAMPLES.length;
    setExampleIndex(next);
    setValues(EXAMPLES[next]!);
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    void analyze(values);
  }

  // the solver recognized a triangle problem: analyze it as soon as the tool opens
  const started = useRef(false);
  useEffect(() => {
    if (start?.run && !started.current) {
      started.current = true;
      void analyze(start.points);
    }
  }, []); // once, when the tool opens

  async function analyze(points: string[][]) {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/triangle", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ points: points.map((r) => r.map((c) => c.trim())) }) });
      const data = (await res.json().catch(() => null)) as (TriangleResponseDto & { error?: { message?: string } }) | null;
      if (!res.ok || !data) {
        setResult(null);
        setError(data?.error?.message ?? t("triangle.unavailable"));
      } else if (!data.ok || !data.data) {
        setResult(null);
        const key = `triangle.error.${data.code ?? "cannot_analyze"}` as MessageKey;
        const text = t(key);
        setError(text === key ? (data.message ?? t("triangle.error.cannot_analyze")) : text);
      } else {
        setResult(data.data);
      }
    } catch {
      setResult(null);
      setError(t("triangle.unavailable"));
    }
    setBusy(false);
  }

  const d = result;
  return (
    <div className="grid gap-6">
      <Card>
        <form onSubmit={submit} className="grid gap-4" aria-labelledby={`${uid}-legend`}>
          <h2 id={`${uid}-legend`} className="text-xl font-bold">
            {t("triangle.vertices")}
          </h2>
          <div className="grid gap-3 sm:grid-cols-3">
            {VERTICES.map((name, row) => (
              <fieldset key={name} className="grid gap-2 rounded-[var(--radius-sm)] border border-line p-3">
                <legend className="px-1 font-bold">{t("triangle.vertex", { name })}</legend>
                <div className="grid grid-cols-2 gap-2">
                  {AXES.map((axis, col) => (
                    <label key={axis} className="grid gap-1 text-sm font-semibold text-muted">
                      <span aria-hidden="true">{axis}</span>
                      <input
                        aria-label={t("triangle.coordinate", { name, axis })}
                        value={values[row]![col]!}
                        onChange={(e) => setValue(row, col, e.target.value)}
                        inputMode="text"
                        autoComplete="off"
                        spellCheck={false}
                        maxLength={24}
                        className={inputClass}
                      />
                    </label>
                  ))}
                </div>
              </fieldset>
            ))}
          </div>
          <p className="text-sm text-muted">
            {t("triangle.hint")} {t("triangle.exact")}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={busy}>
              {busy ? t("triangle.calculating") : t("triangle.calculate")}
            </Button>
            <Button type="button" variant="secondary" onClick={nextExample}>
              {t("triangle.example")}
            </Button>
          </div>
          {error ? (
            <p role="alert" className="rounded-[var(--radius-sm)] bg-warning-soft px-3 py-2 font-medium text-warning">
              {error}
            </p>
          ) : null}
        </form>
      </Card>

      {d ? (
        <div className="grid gap-6" data-testid="triangle-result">
          <nav aria-label={t("triangle.jumpLabel")} className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-muted">{t("triangle.jump")}:</span>
            {(
              [
                ["triangle-measurements", t("triangle.measurements")],
                ["triangle-angles", t("triangle.angles")],
                ["triangle-centers", t("triangle.centers")],
                ["triangle-lines", t("triangle.lines")],
                ["triangle-circles", t("triangle.circles")],
                ["triangle-excircles", t("triangle.excircles")],
              ] as const
            ).map(([id, label]) => (
              <a key={id} href={`#${id}`} className={buttonClass("ghost")}>
                {label}
              </a>
            ))}
          </nav>

          <Section id="triangle-figure" title={t("triangle.figureTitle")}>
            <FigureExplorer figure={buildFigure(d)} />
            <p className="text-sm text-muted">{t("triangle.figureNote")}</p>
          </Section>

          <Section id="triangle-measurements" title={t("triangle.measurements")}>
            <dl className="grid gap-2">
              {d.sides.map((s) => (
                <Row
                  key={s.key}
                  label={`${t("triangle.side", { name: s.name })}${d.longest.includes(s.name) ? ` (${t("triangle.longest")})` : ""}${d.shortest.includes(s.name) && d.shortest.length < 3 ? ` (${t("triangle.shortest")})` : ""}`}
                  html={s.lengthHtml}
                />
              ))}
              <Row label={t("triangle.perimeter")} html={d.perimeterHtml} />
              <Row label={t("triangle.semiperimeter")} html={d.semiperimeterHtml} />
              <Row label={t("triangle.area")} html={d.areaHtml} />
              <Row label={t("triangle.kind")} html={`<span>${t(`triangle.kindSides.${d.kind.by_sides}` as MessageKey)}; ${t(`triangle.kindAngles.${d.kind.by_angles}` as MessageKey)}</span>`} />
            </dl>
          </Section>

          <Section id="triangle-angles" title={t("triangle.angles")}>
            <dl className="grid gap-2">
              {d.angles.map((a) => (
                <Row key={a.vertex} label={t("triangle.angleAt", { vertex: a.vertex })} html={`${a.angleHtml}${a.degreesHtml ? ` = ${a.degreesHtml}` : ""}, ${t("triangle.cos").toLowerCase()} = ${a.cosHtml}`} />
              ))}
            </dl>
          </Section>

          <Section id="triangle-centers" title={t("triangle.centers")}>
            <dl className="grid gap-2">
              {(["G", "I", "O", "H", "N"] as const).map((k) => (
                <Row key={k} label={t(`triangle.centerNames.${k}` as MessageKey)} html={d.centers[k] ?? ""} />
              ))}
              <Row label={t("triangle.inradius")} html={d.radii.rHtml} />
              <Row label={t("triangle.circumradius")} html={d.radii.RHtml} />
            </dl>
            <h3 className="text-lg font-bold">{t("triangle.euler")}</h3>
            {d.euler ? (
              <dl className="grid gap-2">
                {LINE_FORMS.map((form) => (
                  <Row key={form} label={t(`triangle.forms.${form}` as MessageKey)} html={d.euler?.[form] ?? `<span class="text-muted">${t("triangle.noIntercept")}</span>`} />
                ))}
              </dl>
            ) : (
              <p className="text-muted">{t("triangle.noEuler")}</p>
            )}
          </Section>

          <LinesSection d={d} />

          <Section id="triangle-circles" title={t("triangle.circles")}>
            <div className="grid gap-4 lg:grid-cols-2">
              <CircleBlock name={t("triangle.circleNames.incircle")} c={d.circles.incircle} />
              <CircleBlock name={t("triangle.circleNames.circumcircle")} c={d.circles.circumcircle} />
              <CircleBlock name={t("triangle.circleNames.ninepoint")} c={d.circles.ninepoint} />
            </div>
          </Section>

          <Section id="triangle-excircles" title={t("triangle.excircles")}>
            <dl className="grid gap-2">
              {d.excircles.map((e) => (
                <Row key={e.vertex} label={t("triangle.excircleOf", { vertex: e.vertex })} html={`${t("triangle.center")}: ${e.centerHtml}, ${t("triangle.radius").toLowerCase()}: ${e.radiusHtml}`} />
              ))}
            </dl>
          </Section>
        </div>
      ) : null}
    </div>
  );
}
