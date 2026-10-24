"use client";

import Link from "next/link";
import { useId, useState, type FormEvent } from "react";
import { Button, Card, Field, buttonClass, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";

const CATEGORIES = ["problem", "idea", "question", "content", "other"] as const;
const MAX = 2000;

/** The form where a learner writes to the administrators. `page` is the page they came from (a path), sent with the message. */
export function FeedbackForm({ page }: { page: string | null }) {
  const uid = useId();
  const [category, setCategory] = useState<(typeof CATEGORIES)[number]>("problem");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/feedback", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ category, message, page }) });
      const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
      if (!res.ok) setError(data?.error?.message ?? t("auth.errorGeneric"));
      else {
        setSent(true);
        setMessage("");
      }
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <Card className="border-2 border-success">
        <p role="status" className="text-lg font-semibold text-success">
          {t("feedback.thanks")}
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => setSent(false)}>
            {t("feedback.another")}
          </Button>
          <Link href="/dashboard" className={buttonClass("primary")}>
            {t("lesson.back")}
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <form onSubmit={onSubmit} className="grid gap-4">
        <Field label={t("feedback.about")} id={`${uid}-cat`}>
          <select id={`${uid}-cat`} value={category} onChange={(e) => setCategory(e.target.value as (typeof CATEGORIES)[number])} className={inputClass}>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {t(`feedback.cat.${c}`)}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t("feedback.message")} id={`${uid}-msg`} hint={t("feedback.hint", { max: MAX })}>
          <textarea
            id={`${uid}-msg`}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={MAX}
            rows={7}
            required
            className={`${inputClass} min-h-40`}
          />
        </Field>
        {page ? (
          <p className="text-sm text-muted">
            {t("feedback.page")}: <span className="font-mono">{page}</span>
          </p>
        ) : null}
        {error ? (
          <p role="alert" className="font-medium text-danger">
            {error}
          </p>
        ) : null}
        <div>
          <Button type="submit" disabled={busy || message.trim().length < 5}>
            {busy ? t("auth.working") : t("feedback.send")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
