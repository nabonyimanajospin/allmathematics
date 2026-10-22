/**
 * Content verification pipeline (spec section 7.4). Nothing is published unless this passes.
 *   static  : structure rules, KaTeX compile, notation lint, no decimals, length limits
 *   engine  : every worked-example result is recomputed; every answer key checks itself;
 *             multiple-choice has exactly one right option; common mistakes are really wrong
 */

import katex from "katex";
import { validatePlotConfig } from "@allmaths/core";
import { extractMath, getMacros, lintAnswerExpression, lintMath, type LintIssue } from "@allmaths/notation";
import type { ContentIssue } from "./loader";
import { toEngineRequest, type EngineRequestBody } from "./client";
import type { CheckSpec, Exercise, Lesson, Section } from "./schema";

export interface TextField {
  path: string;
  text: string;
  /** Extra display math not delimited by $ in the source (formula blocks). */
  displayMath?: string;
  allowDecimal: boolean;
  lintIgnore: readonly string[];
}

function field(path: string, text: string, s: Section): TextField {
  return { path, text, allowDecimal: s.allowDecimal ?? false, lintIgnore: s.lintIgnore ?? [] };
}

/** Every author-written text of a section, with its path for error messages. */
export function sectionTextFields(s: Section, index: number): TextField[] {
  const p = (k: string) => `sections[${index}](${s.id}).${k}`;
  switch (s.type) {
    case "concept":
      return [...(s.title ? [field(p("title"), s.title, s)] : []), field(p("body"), s.body, s), ...(s.more ? [field(p("more"), s.more, s)] : [])];
    case "definition":
      return [field(p("term"), s.term, s), field(p("body"), s.body, s), ...(s.more ? [field(p("more"), s.more, s)] : [])];
    case "theorem":
      return [
        ...(s.name ? [field(p("name"), s.name, s)] : []),
        field(p("statement"), s.statement, s),
        ...(s.proof ? [field(p("proof"), s.proof, s)] : []),
        ...(s.more ? [field(p("more"), s.more, s)] : []),
      ];
    case "formula":
      return [
        { ...field(p("title"), s.title, s) },
        { ...field(p("formula"), "", s), displayMath: s.formula },
        ...(s.note ? [field(p("note"), s.note, s)] : []),
      ];
    case "example":
      return [
        ...(s.title ? [field(p("title"), s.title, s)] : []),
        field(p("problem"), s.problem, s),
        ...s.steps.flatMap((t, i) =>
          typeof t === "string"
            ? [field(p(`steps[${i}]`), t, s)]
            : [field(p(`steps[${i}]`), t.text, s), field(p(`steps[${i}].why`), t.why, s)],
        ),
        field(p("answer"), s.answer, s),
        ...(s.more ? [field(p("more"), s.more, s)] : []),
      ];
    case "visual":
      return [field(p("title"), s.title, s), field(p("caption"), s.caption, s)];
    case "check":
      return [
        field(p("prompt"), s.prompt, s),
        ...s.hints.map((t, i) => field(p(`hints[${i}]`), t, s)),
        field(p("explanation"), s.explanation, s),
        ...(s.choices ?? []).map((c, i) => field(p(`choices[${i}]`), c.text, s)),
        ...(s.mistakes ?? []).map((m, i) => field(p(`mistakes[${i}].hint`), m.hint, s)),
      ];
    case "summary":
      return s.points.map((t, i) => field(p(`points[${i}]`), t, s));
    case "practice":
      return [];
  }
}

export function exerciseTextFields(lesson: Lesson): TextField[] {
  const out: TextField[] = [];
  lesson.exerciseSets.forEach((set, si) => {
    const base = `exerciseSets[${si}](${set.id})`;
    out.push({ path: `${base}.task`, text: set.task, allowDecimal: false, lintIgnore: [] });
    if (set.format) out.push({ path: `${base}.format`, text: set.format, allowDecimal: false, lintIgnore: [] });
    set.items.forEach((item, ii) => {
      const p = (k: string) => `${base}.items[${ii}](${item.id}).${k}`;
      const f = (k: string, text: string): TextField => ({
        path: p(k),
        text,
        allowDecimal: item.allowDecimal ?? false,
        lintIgnore: item.lintIgnore ?? [],
      });
      out.push(f("statement", item.statement), f("solution", item.solution));
      if (item.note) out.push(f("note", item.note));
      item.hints.forEach((h, i) => out.push(f(`hints[${i}]`, h)));
      (item.choices ?? []).forEach((c, i) => out.push(f(`choices[${i}]`, c.text)));
      (item.mistakes ?? []).forEach((m, i) => out.push(f(`mistakes[${i}].hint`, m.hint)));
    });
  });
  return out;
}

export function lessonTextFields(lesson: Lesson): TextField[] {
  const out: TextField[] = [
    { path: "title", text: lesson.title, allowDecimal: false, lintIgnore: [] },
    ...lesson.objectives.map((o, i) => ({ path: `objectives[${i}]`, text: o, allowDecimal: false, lintIgnore: [] })),
  ];
  lesson.sections.forEach((s, i) => out.push(...sectionTextFields(s, i)));
  out.push(...exerciseTextFields(lesson));
  return out;
}

function compile(latex: string, display: boolean): string | null {
  try {
    katex.renderToString(latex, {
      displayMode: display,
      throwOnError: true,
      strict: "error",
      trust: false,
      macros: getMacros("course"),
    });
    return null;
  } catch (e) {
    return e instanceof Error ? e.message : String(e);
  }
}

/** Words outside math; each math segment counts as one word. */
export function wordCount(text: string): number {
  const stripped = text.replace(/\$\$[\s\S]*?\$\$|\$[^$]*?\$/g, " M ");
  return stripped.split(/\s+/).filter((w) => /[A-Za-z0-9]/.test(w)).length;
}

const MAX_CONCEPT_WORDS_WARN = 250;
const MAX_CONCEPT_WORDS_ERROR = 320;

export function verifyLessonStatic(lesson: Lesson, file: string): ContentIssue[] {
  const issues: ContentIssue[] = [];
  const err = (message: string) => issues.push({ file, message, severity: "error" });
  const warn = (message: string) => issues.push({ file, message, severity: "warning" });

  const types = lesson.sections.map((s) => s.type);
  if (types[types.length - 1] !== "summary") err("The last section of a lesson must be a summary.");
  if (!types.includes("example")) err("A lesson needs at least one worked example.");
  if (!types.includes("check")) err("A lesson needs at least one check question.");
  if (types[0] !== "concept" && types[0] !== "definition") err("A lesson starts with a concept or definition.");

  for (const f of lessonTextFields(lesson)) {
    /* eslint-disable no-control-regex -- the point of this check is to find control characters */
    // A stray control character (for example a form feed made from "\f" in a script) silently breaks a formula.
    if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(f.text) || (f.displayMath !== undefined && /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(f.displayMath))) {
      err(`${f.path}: the text contains a control character (check backslashes such as \\frac or \\text)`);
    }
    /* eslint-enable no-control-regex */
    const sources: { latex: string; display: boolean }[] = [];
    const { segments, unbalanced } = extractMath(f.text);
    if (unbalanced) err(`${f.path}: unbalanced $ in math. Write a literal dollar sign as \\$.`);
    sources.push(...segments);
    if (f.displayMath !== undefined) sources.push({ latex: f.displayMath, display: true });

    for (const seg of sources) {
      const failure = compile(seg.latex, seg.display);
      if (failure) err(`${f.path}: math does not compile (${failure}) in “${seg.latex.slice(0, 60)}”`);
      const lint: LintIssue[] = lintMath(seg.latex, { allowDecimal: f.allowDecimal, display: seg.display });
      for (const li of lint) {
        if (f.lintIgnore.includes(li.rule)) continue;
        const text = `${f.path}: [${li.rule}] ${li.message} (“${li.excerpt}”)`;
        if (li.severity === "error") err(text);
        else warn(text);
      }
    }
    // A stray unescaped LaTeX command outside math, e.g. "\vec u" in prose, would show as plain text.
    const prose = f.text.replace(/\$\$[\s\S]*?\$\$|\$[^$]*?\$/g, " ");
    if (/\\(?:vec|dotp|crossp|boxp|frac|sqrt|norm)\b/.test(prose)) {
      err(`${f.path}: LaTeX outside $...$ (put every formula between dollar signs)`);
    }
  }

  const squash = (t: string): string => t.replace(/\s+/g, "").toLowerCase();
  for (const set of lesson.exerciseSets) {
    // The format hint is shown for the whole set: an example in it must not be the key of one of the exercises.
    const examples = [...(set.format ?? "").matchAll(/`([^`]+)`/g)].map((m) => squash(m[1] ?? ""));
    for (const item of set.items) {
      const where = `exercise ${item.id}`;
      if (examples.includes(squash(item.answer))) err(`exerciseSets(${set.id}).format: the example “${item.answer}” is the answer of ${item.id}`);
      if (item.answerType !== "multiple_choice" && !item.allowDecimal) {
        for (const li of lintAnswerExpression(item.answer)) {
          if (item.lintIgnore?.includes(li.rule)) continue;
          err(`${where}.answer: [${li.rule}] ${li.message} (“${li.excerpt}”)`);
        }
      }
      if (item.hints.length === 0) warn(`${where}: an exercise should have at least one hint.`);
    }
  }

  lesson.sections.forEach((s, i) => {
    if (s.type === "concept") {
      const words = wordCount(s.body);
      if (words > MAX_CONCEPT_WORDS_ERROR) err(`sections[${i}](${s.id}): concept has ${words} words (limit about 250).`);
      else if (words > MAX_CONCEPT_WORDS_WARN) warn(`sections[${i}](${s.id}): concept has ${words} words (aim for at most 250).`);
    }
    if (s.type === "visual" && s.kind === "plot") {
      const problem = validatePlotConfig(s.config ?? {});
      if (problem) err(`sections[${i}](${s.id}): ${problem}`);
    }
    if (s.type === "check" && s.hints.length === 0) warn(`sections[${i}](${s.id}): a check should have at least one hint.`);
    if (s.type === "example") {
      for (const v of s.verify) {
        for (const li of lintAnswerExpression(v.equals)) {
          err(`sections[${i}](${s.id}).verify: [${li.rule}] ${li.message} (“${li.excerpt}”)`);
        }
      }
    }
    if (s.type === "check") {
      for (const li of lintAnswerExpression(s.answer)) {
        err(`sections[${i}](${s.id}).answer: [${li.rule}] ${li.message} (“${li.excerpt}”)`);
      }
    }
  });
  return issues;
}

// ---------------------------------------------------------------------------------------------------
export interface EngineClient {
  verify(a: string, b: string): Promise<{ equal: boolean; code?: string | null; message?: string | null }>;
  check(req: EngineRequestBody): Promise<{ status: "correct" | "incorrect" | "invalid"; code: string; message: string }>;
}

/** Verify one question (a check or an exercise): the key checks itself, mistakes are wrong, choices are unique. */
async function verifyQuestion(
  where: string,
  q: CheckSpec & { allowDecimal?: boolean | undefined },
  engine: EngineClient,
  err: (message: string) => void,
): Promise<void> {
  if (q.answerType === "multiple_choice") {
    const choices = q.choices ?? [];
    for (const [j, c] of choices.entries()) {
      const r = await engine.verify(c.value, q.answer);
      if (r.code) {
        err(`${where}.choices[${j}]: the engine could not evaluate “${c.value}” (${r.code})`);
        continue;
      }
      if (r.equal !== (j === q.correctIndex)) {
        err(
          r.equal
            ? `${where}.choices[${j}]: this option equals the answer but is not the marked correct option`
            : `${where}.choices[${j}]: the marked correct option does not equal the answer`,
        );
      }
    }
    for (let a = 0; a < choices.length; a++) {
      for (let b = a + 1; b < choices.length; b++) {
        const ca = choices[a];
        const cb = choices[b];
        if (!ca || !cb) continue;
        const r = await engine.verify(ca.value, cb.value);
        if (!r.code && r.equal) err(`${where}: options ${a} and ${b} are equal; distractors must all differ`);
      }
    }
    return;
  }
  const self = await engine.check(toEngineRequest(q, q.answer, "text"));
  if (self.status !== "correct") err(`${where}.answer: the key does not check itself (${self.code}: ${self.message})`);
  for (const [j, m] of (q.mistakes ?? []).entries()) {
    const r = await engine.check(toEngineRequest({ ...q, mistakes: undefined }, m.expr, "text"));
    if (r.status === "invalid") err(`${where}.mistakes[${j}]: expression is not valid (${r.code}: ${r.message})`);
    else if (r.status === "correct") err(`${where}.mistakes[${j}]: this “mistake” equals the correct answer`);
  }
}

export async function verifyLessonWithEngine(lesson: Lesson, file: string, engine: EngineClient): Promise<ContentIssue[]> {
  const issues: ContentIssue[] = [];
  const err = (message: string) => issues.push({ file, message, severity: "error" });

  for (const [i, s] of lesson.sections.entries()) {
    const where = `sections[${i}](${s.id})`;
    if (s.type === "example") {
      for (const [j, v] of s.verify.entries()) {
        const r = await engine.verify(v.expr, v.equals);
        if (r.code) err(`${where}.verify[${j}]: the engine could not evaluate it (${r.code}: ${r.message ?? ""}) — ${v.expr}`);
        else if (!r.equal) err(`${where}.verify[${j}]: ${v.expr} is NOT equal to ${v.equals}`);
      }
    }
    if (s.type === "check") await verifyQuestion(where, s, engine, err);
  }
  for (const set of lesson.exerciseSets) {
    for (const item of set.items) {
      const where = `exercise ${item.id}`;
      await verifyQuestion(where, item as Exercise, engine, err);
      for (const [j, v] of (item.verify ?? []).entries()) {
        const r = await engine.verify(v.expr, v.equals);
        if (r.code) err(`${where}.verify[${j}]: the engine could not evaluate it (${r.code}: ${r.message ?? ""}) — ${v.expr}`);
        else if (!r.equal) err(`${where}.verify[${j}]: ${v.expr} is NOT equal to ${v.equals}`);
      }
    }
  }
  return issues;
}
