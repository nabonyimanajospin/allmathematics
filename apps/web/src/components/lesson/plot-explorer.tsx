"use client";

import { useMemo } from "react";
import { buildPlot, type PlotConfig } from "@allmaths/core";

const W = 420;
const PAD = 26;
const COLORS = ["stroke-accent", "stroke-warning", "stroke-success"] as const;
const SWATCH = ["bg-accent", "bg-warning", "bg-success"] as const;

/** A tick step that gives at most about ten marks, from 1, 2, 5, 10, ... */
function tickStep(span: number): number {
  const rough = span / 10;
  const mag = Math.pow(10, Math.floor(Math.log10(rough)));
  const f = rough / mag;
  return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * mag;
}

function ticks(min: number, max: number, step: number): number[] {
  const out: number[] = [];
  for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) out.push(Math.round(v / step) * step);
  return out;
}

/**
 * A curve drawn from its equation: polar, parametric or Cartesian. The axes are marked with whole numbers only.
 * The picture is a help for the eye: the lesson text always states the exact facts in words and formulas.
 */
export function PlotExplorer({ config, title, labelsHtml = {} }: { config: PlotConfig; title: string; labelsHtml?: Record<string, string> }) {
  const result = useMemo(() => {
    try {
      return { plot: buildPlot(config) };
    } catch (e) {
      return { error: e instanceof Error ? e.message : String(e) };
    }
  }, [config]);

  if ("error" in result) return <p role="alert" className="text-warning">{result.error}</p>;
  const { plot } = result;
  const spanX = plot.xmax - plot.xmin;
  const spanY = plot.ymax - plot.ymin;
  const scale = (W - 2 * PAD) / Math.max(spanX, spanY);
  const width = spanX * scale + 2 * PAD;
  const height = spanY * scale + 2 * PAD;
  const px = (x: number) => PAD + (x - plot.xmin) * scale;
  const py = (y: number) => PAD + (plot.ymax - y) * scale;
  const step = tickStep(Math.max(spanX, spanY));
  const xt = ticks(plot.xmin, plot.xmax, step);
  const yt = ticks(plot.ymin, plot.ymax, step);
  const axisX = plot.ymin <= 0 && plot.ymax >= 0 ? py(0) : height - PAD;
  const axisY = plot.xmin <= 0 && plot.xmax >= 0 ? px(0) : PAD;
  const labelled = plot.curves.filter((c) => c.label !== "" && !c.dashed);

  return (
    <figure>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={String(config.alt ?? title)}
        className="mx-auto block w-full max-w-[28rem] rounded-[var(--radius-sm)] bg-surface"
      >
        <g className="stroke-line" strokeWidth="1" opacity="0.7">
          {xt.map((v) => (
            <line key={`gx${v}`} x1={px(v)} x2={px(v)} y1={PAD} y2={height - PAD} />
          ))}
          {yt.map((v) => (
            <line key={`gy${v}`} y1={py(v)} y2={py(v)} x1={PAD} x2={width - PAD} />
          ))}
        </g>
        <g className="stroke-muted" strokeWidth="1.5">
          <line x1={PAD} x2={width - PAD} y1={axisX} y2={axisX} />
          <line x1={axisY} x2={axisY} y1={PAD} y2={height - PAD} />
        </g>
        <g className="fill-muted" fontSize="11">
          {xt.filter((v) => v !== 0).map((v) => (
            <text key={`tx${v}`} x={px(v)} y={Math.min(axisX + 14, height - 8)} textAnchor="middle">
              {v}
            </text>
          ))}
          {yt.filter((v) => v !== 0).map((v) => (
            <text key={`ty${v}`} x={Math.max(axisY - 6, 12)} y={py(v) + 4} textAnchor="end">
              {v}
            </text>
          ))}
        </g>
        {plot.curves.map((c, i) =>
          c.pieces.map((piece, j) => (
            <polyline
              key={`${i}-${j}`}
              className={c.dashed ? "stroke-muted" : COLORS[i % COLORS.length]}
              fill="none"
              strokeDasharray={c.dashed ? "7 6" : undefined}
              strokeWidth={c.dashed ? "1.8" : "2.5"}
              strokeLinejoin="round"
              strokeLinecap="round"
              points={piece.map(([x, y]) => `${px(x).toFixed(1)},${py(y).toFixed(1)}`).join(" ")}
            />
          )),
        )}
      </svg>
      {labelled.length > 0 ? (
        <ul className="mt-2 flex flex-wrap justify-center gap-x-5 gap-y-1 text-sm">
          {plot.curves.map((c, i) =>
            c.label && !c.dashed ? (
              <li key={i} className="flex items-center gap-2">
                <span className={`inline-block h-1 w-6 rounded-full ${SWATCH[i % SWATCH.length]}`} aria-hidden="true" />
                {labelsHtml[`l${i + 1}`] ? <span dangerouslySetInnerHTML={{ __html: labelsHtml[`l${i + 1}`]! }} /> : <span>{c.label}</span>}
              </li>
            ) : null,
          )}
        </ul>
      ) : null}
    </figure>
  );
}
