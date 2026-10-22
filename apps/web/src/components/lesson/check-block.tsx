"use client";

import { useId, useRef, useState, type FormEvent } from "react";
import { Button } from "@allmaths/ui";
import type { CheckResponseDto, LessonStateDto, RSection } from "@/lib/lesson-types";
import { t } from "@/i18n";
import { Rich, RichInline } from "./rich";

type CheckSection = Extract<RSection, { type: "check" }>;

interface Props {
  lessonId: string;
  section: CheckSection;
  completed: boolean;
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

export function CheckBlock({ lessonId, section, completed, hintsUsed, onCorrect }: Props) {
  const uid = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [value, setValue] = useState("");
  const [choice, setChoice] = useState<number | null>(null);
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
    const answer = isChoice ? (choice === null ? "" : String(choice)) : value.trim();
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

  async function nextHint() {
    const r = await post<{ textHtml: string; hintsUsed: number; error?: { message: string } }>(`${base}/hint`, { index: hints.length });
    if (r.ok && r.data) {
      setHints((h) => [...h, r.data!.textHtml]);
      setHintCountUsed(Math.max(hintCountUsed, r.data.hintsUsed));
    }
  }

  async function showSolution() {
    const r = await post<{ explanationHtml: string }>(`${base}/solution`, {});
    if (r.ok && r.data) setExplanation(r.data.explanationHtml);
  }

  function insert(text: string, caret?: number) {
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

  const placeholder =
    section.answerType === "vector" || section.answerType === "point"
      ? t("check.placeholderVector")
      : section.answerType === "expression"
        ? t("check.placeholderExpression")
        : t("check.placeholderNumber");

  const tone =
    feedback.kind === "correct" || completed
      ? "border-success"
      : feedback.kind === "incorrect"
        ? "border-danger"
        : "border-line";

  return (
    <div
      className={`rounded-[var(--radius)] border-2 bg-surface p-5 ${tone} ${shaking ? "shake" : ""}`}
      onAnimationEnd={(e) => {
        if (e.target === e.currentTarget) setShaking(false);
      }}
    >
      <p className="mb-2 text-sm font-bold uppercase tracking-wide text-accent">{t("lesson.check")}</p>
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
            <div className="flex flex-wrap items-center gap-2" role="group" aria-label={t("check.symbols")}>
              {[
                { label: "√", title: t("check.insertRoot"), text: "sqrt()", caret: 5 },
                { label: "a/b", title: t("check.insertFraction"), text: "()/()", caret: 1 },
                { label: "π", title: t("check.insertPi"), text: "pi" },
                { label: "( )", title: "( )", text: "()", caret: 1 },
                { label: "xⁿ", title: "^", text: "^()", caret: 2 },
                { label: ",", title: ",", text: ", " },
                { label: "−", title: "−", text: "-" },
              ].map((b) => (
                <button
                  key={b.label}
                  type="button"
                  disabled={done}
                  title={b.title}
                  aria-label={b.title}
                  onClick={() => insert(b.text, b.caret)}
                  className="min-h-10 min-w-10 rounded-[var(--radius-sm)] border border-line bg-surface-2 px-3 font-mono text-base font-semibold hover:bg-accent-soft disabled:opacity-50"
                >
                  {b.label}
                </button>
              ))}
            </div>
            <p id={`${uid}-note`} className="text-sm text-muted">
              {t("check.exactNote")}
            </p>
          </>
        )}

        <div className="flex flex-wrap items-center gap-2">
          {!done ? (
            <Button type="submit" disabled={busy || (isChoice ? choice === null : value.trim() === "")}>
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
          <p className="mb-1 text-sm font-bold uppercase tracking-wide text-muted">{t("check.explanation")}</p>
          <Rich html={explanation} />
        </div>
      ) : null}
    </div>
  );
}
