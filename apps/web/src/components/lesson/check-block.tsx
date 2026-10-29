"use client";

import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { Button } from "@allmaths/ui";
import type { AnswerKind, CheckResponseDto, LessonStateDto } from "@/lib/lesson-types";
import { t } from "@/i18n";
import { Rich, RichInline } from "./rich";
import { MathField, type MathFieldHandle } from "./math-field";

/** What the block needs of a question: the same for a check inside a lesson and for an exercise. */
export interface Question {
  id: string;
  promptHtml: string;
  answerType: AnswerKind;
  choicesHtml?: string[] | undefined;
  hintCount: number;
}

interface Props {
  lessonId: string;
  section: Question;
  /** Small label above the question; defaults to "Quick check". */
  heading?: string;
  /** Hide the heading and use a lighter frame (exercise lists). */
  compact?: boolean;
  /** Label above the explanation shown after a correct answer ("Explanation" or "Worked solution"). */
  explanationLabel?: string;
  completed: boolean;
  /** For a multiple-choice question that was answered before: the option that was chosen, shown as selected. */
  completedChoice?: number | undefined;
  hintsUsed: number;
  onCorrect: (progress: LessonStateDto["progress"] | undefined) => void;
}

async function post<T>(url: string, body: unknown): Promise<{ ok: boolean; status: number; data: T | null }> {
  try {
    const res = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    const data = (await res.json().catch(() => null)) as T | null;
    return { ok: res.ok, status: res.status, data };
  } catch {
    return { ok: false, status: 0, data: null };
  }
}

type Feedback =
  | { kind: "none" }
  | { kind: "correct"; studentHtml?: string }
  | { kind: "incorrect"; hintHtml?: string; studentHtml?: string; parts?: boolean[] }
  | { kind: "invalid"; message: string }
  | { kind: "error"; message: string };

export function CheckBlock({ lessonId, section, heading, compact = false, explanationLabel, completed, completedChoice, hintsUsed, onCorrect }: Props) {
  const uid = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const mathRef = useRef<MathFieldHandle>(null);
  // The student writes mathematics as printed (fractions stacked); plain text stays available.
  const [textMode, setTextMode] = useState(false);
  useEffect(() => {
    try {
      if (window.localStorage.getItem("answer-mode") === "text") setTextMode(true);
    } catch {
      // storage can be unavailable: the math field is the default
    }
  }, []);
  function switchMode(text: boolean) {
    setTextMode(text);
    setValue("");
    try {
      window.localStorage.setItem("answer-mode", text ? "text" : "math");
    } catch {
      // ignore
    }
  }
  const [value, setValue] = useState("");
  const [choice, setChoice] = useState<number | null>(completedChoice ?? null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<Feedback>({ kind: "none" });
  const [shaking, setShaking] = useState(false);
  const [hints, setHints] = useState<string[]>([]);
  const [hintCountUsed, setHintCountUsed] = useState(hintsUsed);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);

  const base = `/api/lessons/${lessonId}/sections/${section.id}`;
  const isChoice = section.answerType === "multiple_choice";
  const done = completed || feedback.kind === "correct";

  async function submit(e: FormEvent) {
    e.preventDefault();
    const answer = isChoice ? (choice === null ? "" : String(choice)) : value.trim().replaceAll("°", "*(pi/180)");
    if (!answer || busy) return;
    setBusy(true);
    const r = await post<CheckResponseDto & { error?: { message: string } }>(`${base}/check`, { answer });
    setBusy(false);
    if (!r.ok || !r.data) {
      setFeedback({ kind: "error", message: r.data?.error?.message ?? t("check.unavailable") });
      return;
    }
    const d = r.data;
    if (d.status === "correct") {
      setFeedback({ kind: "correct", ...(d.studentLatexHtml ? { studentHtml: d.studentLatexHtml } : {}) });
      if (d.explanationHtml) setExplanation(d.explanationHtml);
      onCorrect(d.progress);
    } else if (d.status === "incorrect") {
      setAttempts((n) => n + 1);
      setShaking(true);
      setFeedback({
        kind: "incorrect",
        ...(d.hintHtml ? { hintHtml: d.hintHtml } : {}),
        ...(d.studentLatexHtml ? { studentHtml: d.studentLatexHtml } : {}),
        ...(d.parts ? { parts: d.parts } : {}),
      });
    } else {
      setFeedback({ kind: "invalid", message: d.message });
    }
  }

  // One hint request at a time, and a hint is stored at its own index: a double click can never show the same hint twice.
  const hintInFlight = useRef(false);
  async function nextHint() {
    if (hintInFlight.current) return;
    hintInFlight.current = true;
    const index = hints.length;
    try {
      const r = await post<{ textHtml: string; hintsUsed: number; error?: { message: string } }>(`${base}/hint`, { index });
      if (r.ok && r.data) {
        const { textHtml, hintsUsed: used } = r.data;
        setHints((h) => (h.length > index ? h : [...h, textHtml]));
        setHintCountUsed((n) => Math.max(n, used));
      }
    } finally {
      hintInFlight.current = false;
    }
  }

  async function showSolution() {
    const r = await post<{ explanationHtml: string }>(`${base}/solution`, {});
    if (r.ok && r.data) setExplanation(r.data.explanationHtml);
  }

  function insert(text: string, caret?: number, latex?: string) {
    if (!textMode) {
      mathRef.current?.insert(latex ?? text);
      return;
    }
    const el = inputRef.current;
    if (!el) return;
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    const next = value.slice(0, start) + text + value.slice(end);
    setValue(next);
    requestAnimationFrame(() => {
      el.focus();
      const pos = start + (caret ?? text.length);
      el.setSelectionRange(pos, pos);
    });
  }

  const placeholder = {
    number: t("check.placeholderNumber"),
    expression: t("check.placeholderExpression"),
    vector: t("check.placeholderVector"),
    point: t("check.placeholderVector"),
    multiple_choice: "",
    region: t("check.placeholderRegion"),
    equation: t("check.placeholderEquation"),
    direction: t("check.placeholderVector"),
    points: t("check.placeholderPoints"),
    ode_solution: t("check.placeholderOde"),
    ode_family: t("check.placeholderFamily"),
  }[section.answerType];

  // The symbol bar offers what the answer type needs, so a phone keyboard is never the obstacle.
  const commonSymbols = [
    { label: "√", title: t("check.insertRoot"), text: "sqrt()", caret: 5, latex: "\\sqrt{#?}" },
    { label: "a/b", title: t("check.insertFraction"), text: "()/()", caret: 1, latex: "\\frac{#?}{#?}" },
    { label: "π", title: t("check.insertPi"), text: "pi", latex: "\\pi" },
    { label: "°", title: t("check.insertDegree"), text: "°", latex: "^{\\circ}" },
    { label: "( )", title: "( )", text: "()", caret: 1, latex: "\\left(#?\\right)" },
    { label: "xⁿ", title: "^", text: "^()", caret: 2, latex: "^{#?}" },
    { label: ",", title: ",", text: ", " },
    { label: "−", title: "−", text: "-" },
  ];
  const extra: Record<string, { label: string; title: string; text: string; caret?: number; latex?: string }[]> = {
    region: [
      { label: "≤", title: "<=", text: "<=", latex: "\\le" },
      { label: "≥", title: ">=", text: ">=", latex: "\\ge" },
      { label: "<", title: "<", text: "<" },
      { label: ">", title: ">", text: ">" },
      { label: "=", title: t("check.symbolEquals"), text: "=" },
      { label: "≠", title: "!=", text: "!=", latex: "\\ne" },
      { label: t("check.symbolAnd"), title: t("check.symbolAnd"), text: " and ", latex: "\\text{ and }" },
      { label: t("check.symbolOr"), title: t("check.symbolOr"), text: " or ", latex: "\\text{ or }" },
    ],
    equation: [{ label: "=", title: t("check.symbolEquals"), text: " = " }],
    ode_solution: [
      { label: "=", title: t("check.symbolEquals"), text: " = " },
      { label: "e^", title: "e^()", text: "e^()", caret: 3, latex: "e^{#?}" },
      { label: "ln", title: "ln()", text: "ln()", caret: 3, latex: "\\ln\\left(#?\\right)" },
      { label: "C", title: t("check.symbolConstant"), text: "C" },
    ],
    ode_family: [
      { label: "=", title: t("check.symbolEquals"), text: " = " },
      { label: "y′", title: t("check.symbolPrime"), text: "y'", latex: "y'" },
      { label: "y″", title: t("check.symbolPrime2"), text: "y''", latex: "y''" },
    ],
  };
  const exactNote = (["number", "expression", "vector", "point", "direction"] as AnswerKind[]).includes(section.answerType);
  const symbols = [...(section.answerType === "multiple_choice" ? [] : commonSymbols), ...(extra[section.answerType] ?? [])];

  const tone =
    feedback.kind === "correct" || completed
      ? "border-success"
      : feedback.kind === "incorrect"
        ? "border-danger"
        : "border-line";

  return (
    <div
      className={`rounded-[var(--radius)] ${compact ? "border" : "border-2"} bg-surface p-5 ${tone} ${shaking ? "shake" : ""}`}
      onAnimationEnd={(e) => {
        if (e.target === e.currentTarget) setShaking(false);
      }}
    >
      {compact ? null : (
        <p className="mb-2 text-sm font-bold uppercase tracking-wide text-accent">{heading ?? t("lesson.check")}</p>
      )}
      <Rich html={section.promptHtml} />

      <form onSubmit={submit} className="mt-4 grid gap-3">
        {isChoice ? (
          <fieldset className="grid gap-2" disabled={done}>
            <legend className="sr-only">{t("check.chooseOne")}</legend>
            {(section.choicesHtml ?? []).map((html, i) => (
              <label
                key={i}
                className={`flex min-h-12 cursor-pointer items-center gap-3 rounded-[var(--radius-sm)] border px-3 py-2 ${
                  choice === i ? "border-accent bg-accent-soft" : "border-line hover:bg-surface-2"
                }`}
              >
                <input type="radio" name={`${uid}-choice`} checked={choice === i} onChange={() => setChoice(i)} className="size-5 accent-[var(--accent)]" />
                <RichInline html={html} className="rich" />
              </label>
            ))}
          </fieldset>
        ) : (
          <>
            <label htmlFor={`${uid}-answer`} className="text-sm font-semibold">
              {t("check.yourAnswer")}
            </label>
            {textMode ? (
              <input
                id={`${uid}-answer`}
                ref={inputRef}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                disabled={done}
                inputMode="text"
                autoComplete="off"
                autoCapitalize="off"
                autoCorrect="off"
                spellCheck={false}
                maxLength={200}
                placeholder={placeholder}
                aria-describedby={`${uid}-note`}
                className="min-h-12 w-full rounded-[var(--radius-sm)] border border-line bg-bg px-3 py-2 font-mono text-lg text-ink placeholder:font-sans placeholder:text-base placeholder:text-muted"
              />
            ) : (
              <MathField
                ref={mathRef}
                id={`${uid}-answer`}
                label={t("check.yourAnswer")}
                disabled={done}
                describedBy={`${uid}-note`}
                onChange={setValue}
                onEnter={() => document.getElementById(`${uid}-submit`)?.click()}
              />
            )}
            {done ? null : (
              <button type="button" onClick={() => switchMode(!textMode)} className="w-fit text-sm font-medium text-accent underline underline-offset-2">
                {textMode ? t("check.modeMath") : t("check.modeText")}
              </button>
            )}
            {done ? null : (
            <div className="flex flex-wrap items-center gap-2" role="group" aria-label={t("check.symbols")}>
              {symbols.map((b) => (
                <button
                  key={b.label}
                  type="button"
                  disabled={done}
                  title={b.title}
                  aria-label={b.label === "a/b" ? undefined : `${b.label} ${b.title}`}
                  onClick={() => insert(b.text, b.caret, b.latex)}
                  className="min-h-10 min-w-10 rounded-[var(--radius-sm)] border border-line bg-surface-2 px-3 font-mono text-base font-semibold hover:bg-accent-soft disabled:opacity-50"
                >
                  {b.label === "a/b" ? (
                    <>
                      <span className="inline-flex flex-col items-center text-xs leading-none" aria-hidden="true">
                        <span>a</span>
                        <span className="my-0.5 h-px w-3.5 bg-current" />
                        <span>b</span>
                      </span>
                      <span className="sr-only">{b.title}</span>
                    </>
                  ) : (
                    b.label
                  )}
                </button>
              ))}
            </div>
            )}
            {exactNote && !done ? (
              <p id={`${uid}-note`} className="text-sm text-muted">
                {t("check.exactNote")}
              </p>
            ) : (
              <span id={`${uid}-note`} className="sr-only">
                {placeholder}
              </span>
            )}
          </>
        )}

        <div className="flex flex-wrap items-center gap-2">
          {!done ? (
            <Button id={`${uid}-submit`} type="submit" disabled={busy || (isChoice ? choice === null : value.trim() === "")}>
              {busy ? t("check.checking") : t("check.submit")}
            </Button>
          ) : null}
          {!done && section.hintCount > 0 ? (
            <Button variant="secondary" onClick={nextHint} disabled={hints.length >= section.hintCount}>
              {hints.length >= section.hintCount
                ? t("check.noMoreHints")
                : t("check.hint", { used: hints.length + 1, total: section.hintCount })}
            </Button>
          ) : null}
          {!done && (attempts >= 1 || hintCountUsed >= section.hintCount) && !explanation ? (
            <Button variant="ghost" onClick={showSolution}>
              {t("check.showSolution")}
            </Button>
          ) : null}
        </div>
      </form>

      {hints.length > 0 ? (
        <ol className="mt-4 grid gap-2">
          {hints.map((h, i) => (
            <li key={i} className="fade-up rounded-[var(--radius-sm)] bg-warning-soft px-3 py-2">
              <Rich html={h} />
            </li>
          ))}
        </ol>
      ) : null}

      <div aria-live="polite" className="mt-3">
        {feedback.kind === "correct" || (completed && feedback.kind === "none") ? (
          <p className="pop inline-flex items-center gap-2 rounded-full bg-success-soft px-3 py-1.5 font-bold text-success">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M5 12.5l4.5 4.5L19 7.5" />
            </svg>
            {t("check.correct")}
          </p>
        ) : null}
        {feedback.kind === "incorrect" ? (
          <div className="fade-up grid gap-2">
            <p className="font-semibold text-danger">{t("check.incorrect")}</p>
            {feedback.hintHtml ? <Rich html={feedback.hintHtml} className="rounded-[var(--radius-sm)] bg-warning-soft px-3 py-2" /> : null}
          </div>
        ) : null}
        {feedback.kind === "invalid" ? (
          <p className="fade-up rounded-[var(--radius-sm)] bg-warning-soft px-3 py-2 font-medium text-warning" role="alert">
            {feedback.message}
          </p>
        ) : null}
        {feedback.kind === "error" ? (
          <p className="fade-up font-medium text-danger" role="alert">
            {feedback.message}
          </p>
        ) : null}
        {(feedback.kind === "incorrect" || feedback.kind === "correct") && feedback.studentHtml ? (
          <p className="mt-2 text-sm text-muted">
            {t("check.yourAnswer")}: <RichInline html={feedback.studentHtml} />
          </p>
        ) : null}
      </div>

      {explanation ? (
        <div className="fade-up mt-4 rounded-[var(--radius-sm)] border border-line bg-surface-2 p-4">
          <p className="mb-1 text-sm font-bold uppercase tracking-wide text-muted">{explanationLabel ?? t("check.explanation")}</p>
          <Rich html={explanation} />
        </div>
      ) : null}
    </div>
  );
}
