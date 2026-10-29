"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button, Card, buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";
import type { StartedTestDto, TestResultDto } from "@/lib/unit-test-types";
import { AnswerInput } from "./lesson/answer-input";
import { Rich, RichInline } from "./lesson/rich";

interface Props {
  unitId: string;
  passScore: number;
  questions: number;
  attempts: number;
  bestScore: number | null;
  passed: boolean;
}

async function post<T>(url: string, body: unknown): Promise<{ ok: boolean; data: (T & { error?: { message?: string } }) | null }> {
  try {
    const res = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    return { ok: res.ok, data: (await res.json().catch(() => null)) as (T & { error?: { message?: string } }) | null };
  } catch {
    return { ok: false, data: null };
  }
}

export function UnitTestRunner({ unitId, passScore, questions, attempts, bestScore, passed }: Props) {
  const router = useRouter();
  const [test, setTest] = useState<StartedTestDto | null>(null);
  const [answers, setAnswers] = useState<string[]>([]);
  const [result, setResult] = useState<TestResultDto | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setBusy(true);
    setError(null);
    setResult(null);
    const r = await post<StartedTestDto>("/api/unit-tests", { unitId });
    setBusy(false);
    if (!r.ok || !r.data) return setError(r.data?.error?.message ?? t("auth.errorGeneric"));
    setTest(r.data);
    setAnswers(r.data.questions.map(() => ""));
    window.scrollTo({ top: 0 });
  }

  async function submit() {
    if (!test) return;
    const blank = answers.filter((a) => a.trim() === "").length;
    if (blank > 0 && !window.confirm(t("unitTest.blankConfirm", { n: blank }))) return;
    setBusy(true);
    setError(null);
    const r = await post<TestResultDto>(`/api/unit-tests/${test.attemptId}/submit`, { answers });
    setBusy(false);
    if (!r.ok || !r.data) return setError(r.data?.error?.message ?? t("auth.errorGeneric"));
    setResult(r.data);
    router.refresh();
    window.scrollTo({ top: 0 });
  }

  if (result && test) {
    return (
      <div>
        <Card className={`border-2 text-center ${result.passed ? "border-success" : "border-danger"}`}>
          <p role="status" className={`text-3xl font-extrabold ${result.passed ? "text-success" : "text-danger"}`}>
            {t("unitTest.score", { score: result.score, total: result.total })}
          </p>
          <p className="mt-2 text-lg font-semibold">{result.passed ? t("unitTest.passed") : t("unitTest.failed", { pass: result.passScore })}</p>
          <div className="mt-4 flex flex-wrap justify-center gap-3">
            <Button variant={result.passed ? "secondary" : "primary"} onClick={start} disabled={busy}>
              {t("unitTest.retry")}
            </Button>
            <Link href="/dashboard" className={buttonClass(result.passed ? "primary" : "secondary")}>
              {t("lesson.back")}
            </Link>
          </div>
        </Card>
        <h2 className="mt-8 text-xl font-bold">{t("unitTest.review")}</h2>
        <ol className="mt-4 grid gap-4">
          {test.questions.map((q) => {
            const r = result.results.find((x) => x.index === q.index);
            return (
              <li key={q.index}>
                <Card className={`border-2 ${r?.correct ? "border-success" : "border-danger"}`}>
                  <p className="text-sm font-bold uppercase tracking-wide text-muted">
                    {t("unitTest.question", { n: q.index + 1 })} · {r?.correct ? t("unitTest.correct") : t("unitTest.incorrect")}
                  </p>
                  {q.taskHtml ? (
                    <p className="mb-1 font-semibold">
                      <RichInline html={q.taskHtml} />
                    </p>
                  ) : null}
                  <Rich html={q.promptHtml} />
                  <details className="mt-3">
                    <summary className="cursor-pointer font-semibold text-accent">{t("unitTest.solution")}</summary>
                    <Rich html={r?.solutionHtml ?? ""} className="mt-2" />
                  </details>
                </Card>
              </li>
            );
          })}
        </ol>
      </div>
    );
  }

  if (!test) {
    return (
      <div>
        <Card>
          <ul className="grid gap-2">
            <li>{t("unitTest.rule1", { n: questions })}</li>
            <li>{t("unitTest.rule2", { pass: passScore, n: questions })}</li>
            <li>{t("unitTest.rule3")}</li>
            <li>{t("unitTest.rule4")}</li>
          </ul>
          {attempts > 0 ? (
            <p className="mt-4 font-semibold">
              {passed ? t("unitTest.statusPassed", { best: bestScore ?? 0, n: questions }) : t("unitTest.statusNotPassed", { best: bestScore ?? 0, n: questions, attempts })}
            </p>
          ) : null}
          {error ? (
            <p role="alert" className="mt-3 text-danger">
              {error}
            </p>
          ) : null}
          <div className="mt-5">
            <Button onClick={start} disabled={busy}>
              {busy ? t("auth.working") : attempts > 0 ? t("unitTest.again") : t("unitTest.start")}
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const answered = answers.filter((a) => a.trim() !== "").length;
  return (
    <div>
      <p className="sticky top-[var(--header-h)] z-20 -mx-4 border-b border-line bg-bg/95 px-4 py-2 text-sm font-semibold tabular-nums backdrop-blur" aria-live="polite">
        {t("unitTest.answered", { done: answered, n: test.questions.length })}
      </p>
      <ol className="mt-4 grid gap-6">
        {test.questions.map((q) => (
          <li key={q.index}>
            <Card>
              <p className="mb-2 text-sm font-bold uppercase tracking-wide text-accent">{t("unitTest.question", { n: q.index + 1 })}</p>
              {q.taskHtml ? (
                <p className="mb-1 font-semibold">
                  <RichInline html={q.taskHtml} />
                </p>
              ) : null}
              <Rich html={q.promptHtml} />
              <div className="mt-3">
                {q.answerType === "multiple_choice" ? (
                  <fieldset className="grid gap-2">
                    <legend className="sr-only">{t("check.chooseOne")}</legend>
                    {(q.choicesHtml ?? []).map((html, i) => (
                      <label
                        key={i}
                        className={`flex min-h-12 cursor-pointer items-center gap-3 rounded-[var(--radius-sm)] border px-3 py-2 ${
                          answers[q.index] === String(i) ? "border-accent bg-accent-soft" : "border-line hover:bg-surface-2"
                        }`}
                      >
                        <input
                          type="radio"
                          name={`q${q.index}-choice`}
                          checked={answers[q.index] === String(i)}
                          onChange={() => setAnswers((a) => a.map((x, k) => (k === q.index ? String(i) : x)))}
                          className="size-5 accent-[var(--accent)]"
                        />
                        <RichInline html={html} className="rich" />
                      </label>
                    ))}
                  </fieldset>
                ) : (
                  <AnswerInput
                    id={`q${q.index}`}
                    answerType={q.answerType}
                    value={answers[q.index] ?? ""}
                    onChange={(v) => setAnswers((a) => a.map((x, i) => (i === q.index ? v : x)))}
                  />
                )}
              </div>
            </Card>
          </li>
        ))}
      </ol>
      {error ? (
        <p role="alert" className="mt-4 text-danger">
          {error}
        </p>
      ) : null}
      <div className="mt-6">
        <Button onClick={submit} disabled={busy}>
          {busy ? t("unitTest.checking") : t("unitTest.submit")}
        </Button>
      </div>
    </div>
  );
}
