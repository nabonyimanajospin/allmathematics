"use client";

import Link from "next/link";
import { useId, useState, type FormEvent } from "react";
import { Button, Card, Field, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";
import { SOLVER_OPERATIONS, type SolveResponseDto, type SolveResultDto, type SolverAccessDto, type SolverOperation } from "@/lib/solver-types";
import { cleanRecognized } from "@/lib/recognized-text";
import { findTriangleVertices } from "@/lib/triangle-input";
import { Rich } from "./lesson/rich";

/** What the solver understands, by topic: each example can be touched to put it in the problem box. */
type SayKey = "derivative" | "integral" | "limit" | "tangent" | "taylor" | "sum" | "area" | "fractions" | "equation" | "system" | "inequality" | "ode" | "factor" | "determinant" | "inverse" | "eigen" | "rref" | "product" | "norm" | "cross" | "partial" | "gradient" | "critical" | "lagrange" | "plane" | "double" | "polar" | "line";
const GROUPS: { key: "calculus" | "equations" | "matrices" | "multivariable"; examples: { say: SayKey; text: string }[] }[] = [
  {
    key: "calculus",
    examples: [
      { say: "derivative", text: "derivative of x^2*sin(x)" },
      { say: "integral", text: "integral of x*e^x from 0 to 1" },
      { say: "limit", text: "limit of sin(x)/x as x->0" },
      { say: "tangent", text: "tangent line to y = x^3 at x = 2" },
      { say: "taylor", text: "taylor series of sin(x) at 0 order 5" },
      { say: "sum", text: "sum of 1/n^2 for n from 1 to infinity" },
      { say: "area", text: "area between y = x and y = x^2" },
      { say: "fractions", text: "partial fractions of (3x+5)/((x-1)(x+2))" },
    ],
  },
  {
    key: "equations",
    examples: [
      { say: "equation", text: "solve x^2-5x+6=0" },
      { say: "system", text: "x+y=5, x-y=1" },
      { say: "inequality", text: "solve (x-1)/(x+2) > 0" },
      { say: "ode", text: "y' + 2y = e^x" },
      { say: "factor", text: "factor x^2 - 9" },
    ],
  },
  {
    key: "matrices",
    examples: [
      { say: "determinant", text: "determinant of [[2,1,0],[1,3,1],[0,1,4]]" },
      { say: "inverse", text: "inverse of [[2,1],[5,3]]" },
      { say: "eigen", text: "eigenvalues and eigenvectors of [[4,1],[2,3]]" },
      { say: "rref", text: "row reduce [[1,2,3],[4,5,6],[7,8,10]]" },
      { say: "product", text: "[[1,2],[3,4]] * [[0,1],[1,0]]" },
      { say: "norm", text: "norm of (3,4)" },
      { say: "cross", text: "cross product of (1,2,3) and (4,5,6)" },
    ],
  },
  {
    key: "multivariable",
    examples: [
      { say: "partial", text: "partial derivative of x^2*y wrt x" },
      { say: "gradient", text: "gradient of x^2*y + z at (1,2,3)" },
      { say: "critical", text: "critical points of x^3 - 3*x*y + y^3" },
      { say: "lagrange", text: "maximize x + y subject to x^2 + y^2 = 1" },
      { say: "plane", text: "tangent plane to z = x^2 + y^2 at (1, 2)" },
      { say: "double", text: "double integral of x*y over x from 0 to 1, y from 0 to x" },
      { say: "polar", text: "double integral of x^2 + y^2 in polar coordinates over r from 0 to 2, theta from 0 to 2*pi" },
      { say: "line", text: "line integral of (-y, x) along (cos(t), sin(t)) for t from 0 to 2*pi" },
    ],
  },
];

/** Problems with what the learner typed: they all get the same short headline. */
const INPUT_CODES = new Set(["parse", "unknown_word", "empty", "no_intent", "bad_vectors", "vector_args", "bad_variables", "bad_point", "bad_bounds", "bad_curve", "undefined", "bad_matrix", "ambiguous", "bad_system", "bad_operation", "too_long", "invalid_input", "invalid_json"]);

const SYMBOLS = ["^", "*", "/", "(", ")", ",", "sqrt()", "pi", "->"];

function AccessLine({ access }: { access: SolverAccessDto }) {
  if (access.premium) return <p className="rounded-full bg-success-soft px-3 py-1 text-sm font-semibold text-success">{t("solver.premium")}</p>;
  return (
    <p className="rounded-full bg-surface-2 px-3 py-1 text-sm font-semibold tabular-nums">
      {t("solver.freeLeft", { left: access.remaining ?? 0, limit: access.limit ?? 0 })}
    </p>
  );
}

export function SolverClient({ initialAccess, canPay, justPaid, onTriangle }: { initialAccess: SolverAccessDto; canPay: boolean; justPaid: boolean; onTriangle?: (points: string[][]) => void }) {
  const uid = useId();
  const [input, setInput] = useState("");
  // a triangle problem typed in the box (three points): the triangle toolkit is offered
  const triangle = findTriangleVertices(input);
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
          {triangle && onTriangle ? (
            <div role="status" className="grid gap-2 rounded-[var(--radius-sm)] border-2 border-accent bg-accent-soft p-3">
              <p className="font-semibold">{t("solver.triangleAsk")}</p>
              <div>
                <Button type="button" onClick={() => onTriangle(triangle)}>
                  {t("solver.triangleAskButton")}
                </Button>
              </div>
            </div>
          ) : onTriangle ? (
            <p className="text-sm text-muted">{t("solver.triangleAskTab")}</p>
          ) : null}
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
        <details className="mt-5 rounded-[var(--radius-sm)] border border-line bg-surface-2 p-3">
          <summary className="cursor-pointer font-semibold text-accent">{t("solver.howTo")}</summary>
          <p className="mt-2 text-sm text-muted">{t("solver.howToTip")}</p>
          <div className="mt-3 grid gap-4">
            {GROUPS.map((g) => (
              <section key={g.key} aria-label={t(`solver.groups.${g.key}`)}>
                <h3 className="text-sm font-bold">{t(`solver.groups.${g.key}`)}</h3>
                <ul className="mt-2 grid gap-1.5">
                  {g.examples.map((ex) => (
                    <li key={ex.say} className="grid gap-0.5 sm:grid-cols-[11rem_minmax(0,1fr)] sm:items-center sm:gap-3">
                      <span className="text-sm text-muted">{t(`solver.say.${ex.say}`)}</span>
                      <button
                        type="button"
                        onClick={() => {
                          setInput(ex.text);
                          setOperation("auto");
                        }}
                        className="min-w-0 break-words rounded-[var(--radius-sm)] border border-line bg-surface px-2 py-1.5 text-left font-mono text-sm hover:bg-accent-soft"
                      >
                        {ex.text}
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </details>
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
