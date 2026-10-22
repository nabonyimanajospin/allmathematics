/**
 * Markdown + KaTeX rendering, on the server. Raw HTML in content is escaped (never trusted), math is
 * rendered with the notation macros, and the result is the only HTML the lesson components inject.
 */

import katex from "katex";
import { Marked } from "marked";
import { getMacros } from "@allmaths/notation";
import { DEFAULT_MIN_SECONDS, requiredSeconds } from "@allmaths/core";
import type { ClientSection, ClientLesson, ClientExerciseSet } from "@allmaths/content-schema";
import type { RExerciseSet, RLesson, RSection } from "@/lib/lesson-types";
import { t } from "@/i18n";

const escapeHtml = (s: string): string =>
  s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

const marked = new Marked({
  gfm: true,
  breaks: false,
  renderer: {
    // content is trusted but still never allowed to inject markup
    html: (token) => escapeHtml(token.text),
  },
});

export function renderMath(latex: string, display: boolean): string {
  const html = katex.renderToString(latex, {
    displayMode: display,
    throwOnError: false,
    output: "htmlAndMathml",
    trust: false,
    strict: "ignore",
    macros: getMacros("course"),
  });
  // A wide equation scrolls sideways on a phone; the scroll box must be reachable with the keyboard (WCAG 2.1.1).
  return display ? `<span class="math-scroll" tabindex="0" role="group" aria-label="${t("lesson.equation")}">${html}</span>` : html;
}

const PLACEHOLDER = (i: number) => `MATHPLACEHOLDER${i}X`;
const cache = new Map<string, string>();

interface Split {
  text: string;
  math: { latex: string; display: boolean }[];
}

function splitMath(src: string): Split {
  const math: Split["math"] = [];
  let out = "";
  let i = 0;
  while (i < src.length) {
    const ch = src[i];
    if (ch === "\\" && src[i + 1] === "$") {
      out += "$"; // escaped dollar becomes a literal dollar sign
      i += 2;
      continue;
    }
    if (ch !== "$") {
      out += ch;
      i++;
      continue;
    }
    const display = src[i + 1] === "$";
    const open = display ? 2 : 1;
    let j = i + open;
    let end = -1;
    while (j < src.length) {
      if (src[j] === "\\") {
        j += 2;
        continue;
      }
      if (src[j] === "$" && (!display || src[j + 1] === "$")) {
        end = j;
        break;
      }
      j++;
    }
    if (end < 0) {
      out += src.slice(i);
      break;
    }
    math.push({ latex: src.slice(i + open, end), display });
    out += PLACEHOLDER(math.length - 1);
    i = end + open;
  }
  return { text: out, math };
}

function restore(html: string, math: Split["math"]): string {
  return html.replace(/MATHPLACEHOLDER(\d+)X/g, (_m, n: string) => {
    const m = math[Number(n)];
    return m ? renderMath(m.latex, m.display) : "";
  });
}

/** Block Markdown (paragraphs, lists, emphasis) with math. */
export function renderRich(src: string): string {
  const key = `b:${src}`;
  const hit = cache.get(key);
  if (hit !== undefined) return hit;
  const { text, math } = splitMath(src.trim());
  const html = restore(marked.parse(text, { async: false }), math);
  if (cache.size > 2000) cache.clear();
  cache.set(key, html);
  return html;
}

/** Inline Markdown with math, without a wrapping paragraph (titles, list items, table cells). */
export function renderInline(src: string): string {
  const key = `i:${src}`;
  const hit = cache.get(key);
  if (hit !== undefined) return hit;
  const { text, math } = splitMath(src.trim());
  const html = restore(marked.parseInline(text, { async: false }), math);
  if (cache.size > 2000) cache.clear();
  cache.set(key, html);
  return html;
}

export function renderStudentLatex(latex: string): string {
  return renderMath(latex, false);
}

function reqSeconds(s: ClientSection): number | null {
  if (s.type === "check") return null;
  const secs = requiredSeconds({ type: s.type, minSeconds: s.minSeconds });
  return Number.isFinite(secs) ? secs : (DEFAULT_MIN_SECONDS[s.type] ?? 15);
}

export function renderSection(s: ClientSection): RSection | null {
  const base = { id: s.id, requiredSeconds: reqSeconds(s) };
  switch (s.type) {
    case "concept":
      return {
        ...base,
        type: "concept",
        ...(s.title ? { titleHtml: renderInline(s.title) } : {}),
        bodyHtml: renderRich(s.body),
        ...(s.more ? { moreHtml: renderRich(s.more) } : {}),
      };
    case "definition":
      return {
        ...base,
        type: "definition",
        termHtml: renderInline(s.term),
        bodyHtml: renderRich(s.body),
        ...(s.more ? { moreHtml: renderRich(s.more) } : {}),
      };
    case "theorem":
      return {
        ...base,
        type: "theorem",
        ...(s.name ? { nameHtml: renderInline(s.name) } : {}),
        statementHtml: renderRich(s.statement),
        ...(s.proof ? { proofHtml: renderRich(s.proof) } : {}),
        ...(s.more ? { moreHtml: renderRich(s.more) } : {}),
      };
    case "formula":
      return {
        ...base,
        type: "formula",
        titleHtml: renderInline(s.title),
        formulaHtml: renderMath(s.formula, true),
        ...(s.note ? { noteHtml: renderRich(s.note) } : {}),
      };
    case "example":
      return {
        ...base,
        type: "example",
        ...(s.title ? { titleHtml: renderInline(s.title) } : {}),
        problemHtml: renderRich(s.problem),
        steps: s.steps.map((st) =>
          typeof st === "string" ? { html: renderRich(st) } : { html: renderRich(st.text), whyHtml: renderRich(st.why) },
        ),
        answerHtml: renderRich(s.answer),
        ...(s.more ? { moreHtml: renderRich(s.more) } : {}),
      };
    case "visual":
      return {
        ...base,
        type: "visual",
        kind: s.kind,
        mode: String(s.config?.mode ?? "components"),
        titleHtml: renderInline(s.title),
        captionHtml: renderRich(s.caption),
      };
    case "check":
      return {
        ...base,
        type: "check",
        promptHtml: renderRich(s.prompt),
        answerType: s.answerType,
        ...(s.choices ? { choicesHtml: s.choices.map((c) => renderInline(c.text)) } : {}),
        hintCount: s.hintCount,
      };
    case "summary":
      return { ...base, type: "summary", pointsHtml: s.points.map(renderRich) };
    case "practice":
      return null;
  }
}

export function renderExerciseSet(set: ClientExerciseSet): RExerciseSet {
  return {
    id: set.id,
    taskHtml: renderRich(set.task),
    ...(set.format ? { formatHtml: renderRich(set.format) } : {}),
    ...(set.source ? { source: set.source } : {}),
    items: set.items.map((e) => ({
      id: e.id,
      statementHtml: renderRich(e.statement),
      answerType: e.answerType,
      ...(e.choices ? { choicesHtml: e.choices.map((c) => renderInline(c.text)) } : {}),
      hintCount: e.hintCount,
      ...(e.note ? { noteHtml: renderRich(e.note) } : {}),
    })),
  };
}

export function renderLesson(lesson: ClientLesson): RLesson {
  return {
    id: lesson.id,
    title: lesson.title,
    estMinutes: lesson.estMinutes,
    objectivesHtml: lesson.objectives.map(renderInline),
    exerciseSets: lesson.exerciseSets.map(renderExerciseSet),
    sections: lesson.sections.flatMap((s) => {
      const r = renderSection(s);
      return r ? [r] : [];
    }),
  };
}
