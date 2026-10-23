"use client";

import Link from "next/link";
import { useId, useState, type FormEvent } from "react";
import { Button, Card, Field, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";
import { SOLVER_OPERATIONS, type SolveResponseDto, type SolveResultDto, type SolverAccessDto, type SolverOperation } from "@/lib/solver-types";
import { cleanRecognized } from "@/lib/recognized-text";
import { Rich } from "./lesson/rich";

const EXAMPLES = [
  "derivative of x^2*sin(x)",
  "integral of x*e^x from 0 to 1",
  "limit of sin(x)/x as x->0",
  "solve x^2-5x+6=0",
  "x+y=5, x-y=1",
  "y' + 2y = e^x",
  "norm of (3,4)",
];

/** Problems with what the learner typed: they all get the same short headline. */
const INPUT_CODES = new Set(["parse", "unknown_word", "empty", "no_intent", "bad_vectors", "vector_args", "ambiguous", "bad_system", "bad_operation", "too_long", "invalid_input", "invalid_json"]);

const SYMBOLS = ["^", "*", "/", "(", ")", "sqrt()", "pi", "->"];

function AccessLine({ access }: { access: SolverAccessDto }) {
  if (access.premium) return <p className="rounded-full bg-success-soft px-3 py-1 text-sm font-semibold text-success">{t("solver.premium")}</p>;
  return (
    <p className="rounded-full bg-surface-2 px-3 py-1 text-sm font-semibold tabular-nums">
      {t("solver.freeLeft", { left: access.remaining ?? 0, limit: access.limit ?? 0 })}
    </p>
  );
}

export function SolverClient({ initialAccess, canPay, justPaid }: { initialAccess: SolverAccessDto; canPay: boolean; justPaid: boolean }) {
  const uid = useId();
  const [input, setInput] = useState("");
  const [operation, setOperation] = useState<SolverOperation>("auto");
  const [busy, setBusy] = useState(false);
  const [access, setAccess] = useState(initialAccess);
  const [result, setResult] = useState<SolveResultDto | null>(null);
  const [error, setError] = useState<{ code: string; message: string } | null>(null);
  const [paying, setPaying] = useState(false);
  const [reading, setReading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  /** Reads the text of a picture on the learner's device (Tesseract); the text is only a draft the learner checks. */
  async function onPicture(file: File | undefined) {
    if (!file) return;
    setError(null);
    setNotice(null);
    if (file.size > 4 * 1024 * 1024) {
      setError({ code: "invalid_input", message: t("solver.photoBig") });
      return;
    }
    setReading(true);
    try {
      const { recognize } = await import("tesseract.js");
      const out = await recognize(file, "eng");
      const text = cleanRecognized(out.data.text);
      if (text === "") setError({ code: "invalid_input", message: t("solver.photoFail") });
      else {
        setInput(text.slice(0, 300));
        setNotice(t("solver.photoDone"));
      }
    } catch {
      setError({ code: "invalid_input", message: t("solver.photoFail") });
    }
    setReading(false);
  }

  async function pay() {
    setPaying(true);
    try {
      const res = await fetch("/api/payments/checkout", { method: "POST" });
      const data = (await res.json().catch(() => null)) as { link?: string; error?: { message?: string } } | null;
      if (res.ok && data?.link) {
        window.location.assign(data.link);
        return;
      }
      setError({ code: "payment", message: data?.error?.message ?? t("auth.errorGeneric") });
    } catch {
      setError({ code: "network", message: t("auth.errorNetwork") });
    }
    setPaying(false);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (busy || input.trim() === "") return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/solver", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ input, operation }) });
      const data = (await res.json().catch(() => null)) as (SolveResponseDto & { error?: { code?: string; message?: string } }) | null;
      if (!res.ok || !data) {
        if (res.status === 402) setAccess((a) => ({ ...a, remaining: 0 }));
        setError({ code: data?.error?.code ?? "error", message: data?.error?.message ?? t("auth.errorGeneric") });
      } else if (!data.ok || !data.solution) {
        setAccess(data.access);
        setError({ code: data.code ?? "cannot_solve", message: data.message ?? t("auth.errorGeneric") });
      } else {
        setAccess(data.access);
        setResult(data.solution);
      }
    } catch {
      setError({ code: "network", message: t("auth.errorNetwork") });
    } finally {
      setBusy(false);
    }
  }

  const limitReached = error?.code === "limit_reached" || (!access.premium && access.remaining === 0);
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-muted">{t("solver.lead")}</p>
        <AccessLine access={access} />
      </div>

      <Card className="mt-6">
        <form onSubmit={onSubmit} className="grid gap-4">
          <Field label={t("solver.operation")} id={`${uid}-op`}>
            <select id={`${uid}-op`} value={operation} onChange={(e) => setOperation(e.target.value as SolverOperation)} className={inputClass}>
              {SOLVER_OPERATIONS.map((o) => (
                <option key={o} value={o}>
                  {t(`solver.ops.${o}`)}
                </option>
              ))}
            </select>
          </Field>
          <Field label={t("solver.problem")} id={`${uid}-input`} hint={t("solver.tips")}>
            <input
              id={`${uid}-input`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              maxLength={300}
              autoComplete="off"
              autoCapitalize="off"
              spellCheck={false}
              placeholder={t("solver.placeholder")}
              className={`${inputClass} font-mono`}
            />
          </Field>
          <div className="flex flex-wrap gap-2" role="group" aria-label={t("check.symbols")}>
            {SYMBOLS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setInput((v) => v + s)}
                className="min-h-10 min-w-10 rounded-[var(--radius-sm)] border border-line bg-surface-2 px-3 font-mono font-semibold hover:bg-accent-soft"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="grid gap-1">
            <label htmlFor={`${uid}-pic`} className="text-sm font-semibold">
              {t("solver.photo")}
            </label>
            <input
              id={`${uid}-pic`}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              disabled={reading}
              onChange={(e) => {
                void onPicture(e.target.files?.[0]);
                e.target.value = "";
              }}
              className="text-sm file:mr-3 file:min-h-10 file:rounded-[var(--radius-sm)] file:border file:border-line file:bg-surface-2 file:px-3 file:font-semibold"
            />
            <p className="text-sm text-muted">{reading ? t("solver.photoReading") : t("solver.photoHint")}</p>
            {notice ? (
              <p role="status" className="text-sm font-medium text-success">
                {notice}
              </p>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={busy || input.trim() === "" || limitReached}>
              {busy ? t("solver.solving") : t("solver.solve")}
            </Button>
          </div>
        </form>
        <div className="mt-5">
          <p className="text-sm font-semibold text-muted">{t("solver.examples")}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => {
                  setInput(ex);
                  setOperation("auto");
                }}
                className="rounded-full border border-line bg-surface px-3 py-1.5 font-mono text-sm hover:bg-accent-soft"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {justPaid ? (
        <p role="status" className="mt-4 rounded-[var(--radius-sm)] bg-success-soft px-3 py-2 font-medium text-success">
          {t("solver.paidThanks")}
        </p>
      ) : null}
      {!access.premium && access.remaining === 0 ? (
        <Card className="mt-4 border-2 border-warning">
          <p className="font-semibold">{t("solver.upgrade")}</p>
          {canPay ? (
            <Button className="mt-3" onClick={pay} disabled={paying}>
              {paying ? t("solver.paying") : t("solver.pay")}
            </Button>
          ) : (
            <p className="mt-2 text-sm text-muted">{t("solver.payOff")}</p>
          )}
        </Card>
      ) : null}

      <div aria-live="polite" className="mt-6">
        {error ? (
          <Card className={`border-2 ${error.code === "limit_reached" ? "border-warning" : "border-danger"}`}>
            <p role="alert" className="font-semibold">
              {INPUT_CODES.has(error.code) ? t("solver.checkInput") : error.message}
            </p>
            {INPUT_CODES.has(error.code) ? <p className="mt-1 text-muted">{error.message}</p> : null}
            {error.code === "limit_reached" ? <p className="mt-2 text-muted">{t("solver.upgrade")}</p> : null}
          </Card>
        ) : null}

        {result ? (
          <div className="grid gap-4">
            <Card>
              <p className="text-sm font-semibold uppercase tracking-wide text-muted">{t("solver.problemLabel")}</p>
              <Rich html={result.questionHtml} />
            </Card>
            <Card>
              <h2 className="text-xl font-bold">{t("solver.steps")}</h2>
              <ol className="mt-3 grid gap-4">
                {result.steps.map((s, i) => (
                  <li key={i} className="grid gap-1">
                    <p className="font-medium">
                      <span className="mr-2 font-bold tabular-nums text-accent">{i + 1}.</span>
                      {s.title}
                    </p>
                    {s.html ? <Rich html={s.html} /> : null}
                  </li>
                ))}
              </ol>
            </Card>
            <Card className="border-2 border-success">
              <p className="text-sm font-semibold uppercase tracking-wide text-success">{t("solver.answer")}</p>
              <Rich html={result.answerHtml} />
              <p className="mt-1 font-mono text-sm text-muted">{result.answerText}</p>
            </Card>
            {result.notes.length > 0 ? (
              <ul className="list-disc pl-6 text-sm text-muted">
                {result.notes.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            ) : null}
            <p className="text-sm text-muted">
              {t("solver.learnMore")}{" "}
              <Link href="/dashboard" className="font-semibold text-accent underline">
                {t("lesson.back")}
              </Link>
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
