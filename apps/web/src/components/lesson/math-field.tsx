"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import type { MathfieldElement } from "mathlive";
import { latexToEngine } from "@/lib/latex-input";

export interface MathFieldHandle {
  /** Insert LaTeX at the caret; `#?` marks a place the student fills next. */
  insert(latex: string): void;
  focus(): void;
}

interface Props {
  id: string;
  label: string;
  placeholder?: string;
  disabled: boolean;
  describedBy?: string;
  onChange: (engineText: string) => void;
  onEnter: () => void;
}

/**
 * A field where the student writes mathematics as it is printed: a fraction is typed with `/` and appears as a
 * numerator over a denominator. The value handed to the page is the plain text the math engine reads.
 */
export const MathField = forwardRef<MathFieldHandle, Props>(function MathField(
  { id, label, placeholder, disabled, describedBy, onChange, onEnter },
  ref,
) {
  const host = useRef<HTMLDivElement>(null);
  const field = useRef<MathfieldElement | null>(null);
  const disabledRef = useRef(disabled);
  disabledRef.current = disabled;
  const cbs = useRef({ onChange, onEnter });
  cbs.current = { onChange, onEnter };

  useImperativeHandle(ref, () => ({
    insert(latex) {
      field.current?.focus();
      field.current?.insert(latex, { focus: true, feedback: false, selectionMode: "placeholder" });
    },
    focus() {
      field.current?.focus();
    },
  }));

  useEffect(() => {
    let cancelled = false;
    let el: MathfieldElement | null = null;
    void import("mathlive").then(({ MathfieldElement }) => {
      if (cancelled || !host.current) return;
      MathfieldElement.fontsDirectory = "/mathlive/fonts";
      MathfieldElement.soundsDirectory = null;
      el = new MathfieldElement();
      el.id = id;
      el.mathVirtualKeyboardPolicy = "manual";
      el.smartFence = true;
      el.setAttribute("aria-label", label);
      if (describedBy) el.setAttribute("aria-describedby", describedBy);
      if (placeholder) el.setAttribute("placeholder", placeholder);
      el.addEventListener("input", () => cbs.current.onChange(latexToEngine(el?.getValue("latex") ?? "")));
      el.addEventListener("keydown", (e) => {
        if ((e as KeyboardEvent).key === "Enter") {
          e.preventDefault();
          cbs.current.onEnter();
        }
      });
      el.readOnly = disabledRef.current;
      el.className = "math-answer";
      field.current = el;
      host.current.appendChild(el);
    });
    return () => {
      cancelled = true;
      el?.remove();
      field.current = null;
    };
    // The element is created once; label and placeholder do not change while the question is shown.
  }, []);

  useEffect(() => {
    if (field.current) field.current.readOnly = disabled;
  }, [disabled]);

  return <div ref={host} className="math-answer-host" />;
});
