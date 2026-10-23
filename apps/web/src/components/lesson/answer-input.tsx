"use client";

import { useEffect, useRef, useState } from "react";
import type { AnswerKind } from "@/lib/lesson-types";
import { t } from "@/i18n";
import { MathField, type MathFieldHandle } from "./math-field";

interface Sym {
  label: string;
  title: string;
  text: string;
  caret?: number;
  latex?: string;
}

/** The symbol bar offers what the answer type needs, so a phone keyboard is never the obstacle. */
export function symbolsFor(answerType: AnswerKind): Sym[] {
  if (answerType === "multiple_choice") return [];
  const common: Sym[] = [
    { label: "√", title: t("check.insertRoot"), text: "sqrt()", caret: 5, latex: "\\sqrt{#?}" },
    { label: "a/b", title: t("check.insertFraction"), text: "()/()", caret: 1, latex: "\\frac{#?}{#?}" },
    { label: "π", title: t("check.insertPi"), text: "pi", latex: "\\pi" },
    { label: "°", title: t("check.insertDegree"), text: "°", latex: "^{\\circ}" },
    { label: "( )", title: "( )", text: "()", caret: 1, latex: "\\left(#?\\right)" },
    { label: "xⁿ", title: "^", text: "^()", caret: 2, latex: "^{#?}" },
    { label: ",", title: ",", text: ", " },
    { label: "−", title: "−", text: "-" },
  ];
  const extra: Record<string, Sym[]> = {
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
  return [...common, ...(extra[answerType] ?? [])];
}

const PLACEHOLDERS: Record<AnswerKind, () => string> = {
  number: () => t("check.placeholderNumber"),
  expression: () => t("check.placeholderExpression"),
  vector: () => t("check.placeholderVector"),
  point: () => t("check.placeholderVector"),
  multiple_choice: () => "",
  region: () => t("check.placeholderRegion"),
  equation: () => t("check.placeholderEquation"),
  direction: () => t("check.placeholderVector"),
  points: () => t("check.placeholderPoints"),
  ode_solution: () => t("check.placeholderOde"),
  ode_family: () => t("check.placeholderFamily"),
};

interface Props {
  id: string;
  answerType: AnswerKind;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  onEnter?: () => void;
}

/**
 * The field where a student types an answer: mathematics as printed (a fraction is written with a slash and shows stacked), with a plain
 * text mode and a symbol bar. Used by the unit tests, where there is no feedback until the whole test is submitted.
 */
export function AnswerInput({ id, answerType, value, onChange, disabled = false, onEnter }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const mathRef = useRef<MathFieldHandle>(null);
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
    onChange("");
    try {
      window.localStorage.setItem("answer-mode", text ? "text" : "math");
    } catch {
      // ignore
    }
  }

  function insert(s: Sym) {
    if (!textMode) {
      mathRef.current?.insert(s.latex ?? s.text);
      return;
    }
    const el = inputRef.current;
    if (!el) return;
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    onChange(value.slice(0, start) + s.text + value.slice(end));
    requestAnimationFrame(() => {
      el.focus();
      const pos = start + (s.caret ?? s.text.length);
      el.setSelectionRange(pos, pos);
    });
  }

  const placeholder = PLACEHOLDERS[answerType]();
  const note = `${id}-note`;
  return (
    <div className="grid gap-3">
      {textMode ? (
        <input
          id={id}
          ref={inputRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          inputMode="text"
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          maxLength={200}
          placeholder={placeholder}
          aria-describedby={note}
          className="min-h-12 w-full rounded-[var(--radius-sm)] border border-line bg-bg px-3 py-2 font-mono text-lg text-ink placeholder:font-sans placeholder:text-base placeholder:text-muted"
        />
      ) : (
        <MathField ref={mathRef} id={id} label={t("check.yourAnswer")} disabled={disabled} describedBy={note} onChange={onChange} onEnter={onEnter ?? (() => undefined)} />
      )}
      {disabled ? null : (
        <button type="button" onClick={() => switchMode(!textMode)} className="w-fit text-sm font-medium text-accent underline underline-offset-2">
          {textMode ? t("check.modeMath") : t("check.modeText")}
        </button>
      )}
      {disabled ? null : (
        <div className="flex flex-wrap items-center gap-2" role="group" aria-label={t("check.symbols")}>
          {symbolsFor(answerType).map((b) => (
            <button
              key={b.label}
              type="button"
              title={b.title}
              aria-label={b.label === "a/b" ? undefined : `${b.label} ${b.title}`}
              onClick={() => insert(b)}
              className="min-h-10 min-w-10 rounded-[var(--radius-sm)] border border-line bg-surface-2 px-3 font-mono text-base font-semibold hover:bg-accent-soft"
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
      <p id={note} className="text-sm text-muted">
        {t("check.exactNote")}
      </p>
    </div>
  );
}
