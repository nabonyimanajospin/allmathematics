"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useState, type FormEvent } from "react";
import { Button, Card, Field, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";

async function post(url: string, payload: unknown): Promise<string | null> {
  try {
    const res = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
    if (res.ok) return null;
    const body = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
    return body?.error?.message ?? t("auth.errorGeneric");
  } catch {
    return t("auth.errorNetwork");
  }
}

/** Step 1: ask for a code by e-mail. Step 2: enter the code and a new password. */
export function ForgotForm() {
  const router = useRouter();
  const uid = useId();
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onRequest(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    const address = String(new FormData(e.currentTarget).get("email") ?? "");
    const err = await post("/api/auth/forgot", { email: address });
    setBusy(false);
    if (err) return setError(err);
    setEmail(address);
    setStep(2);
  }

  async function onReset(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    const f = new FormData(e.currentTarget);
    const err = await post("/api/auth/reset", { email, code: String(f.get("code") ?? ""), password: String(f.get("password") ?? "") });
    setBusy(false);
    if (err) return setError(err);
    router.replace("/signin?reset=1");
  }

  const alert = error ? (
    <p role="alert" className="rounded-[var(--radius-sm)] bg-danger-soft px-3 py-2 text-sm font-medium text-danger">
      {error}
    </p>
  ) : null;

  return (
    <div className="mx-auto max-w-md px-4 py-10">
      <Card className="p-6 sm:p-8">
        <h1 className="text-2xl font-bold tracking-tight">{t("auth.forgotTitle")}</h1>
        {step === 1 ? (
          <form onSubmit={onRequest} className="mt-6 grid gap-4">
            <p className="text-sm text-muted">{t("auth.forgotLead")}</p>
            <Field label={t("auth.email")} id={`${uid}-email`}>
              <input id={`${uid}-email`} name="email" type="email" required maxLength={254} autoComplete="email" inputMode="email" className={inputClass} />
            </Field>
            {alert}
            <Button type="submit" disabled={busy} className="w-full">
              {busy ? t("auth.working") : t("auth.sendCode")}
            </Button>
          </form>
        ) : (
          <form onSubmit={onReset} className="mt-6 grid gap-4">
            <p role="status" className="text-sm text-muted">
              {t("auth.codeSent")}
            </p>
            <Field label={t("auth.code")} id={`${uid}-code`}>
              <input id={`${uid}-code`} name="code" required inputMode="numeric" pattern="\d{6}" maxLength={6} autoComplete="one-time-code" className={inputClass} />
            </Field>
            <Field label={t("auth.newPassword")} id={`${uid}-password`} hint={t("auth.passwordHint")}>
              <input id={`${uid}-password`} name="password" type="password" required minLength={10} maxLength={128} autoComplete="new-password" className={inputClass} />
            </Field>
            {alert}
            <Button type="submit" disabled={busy} className="w-full">
              {busy ? t("auth.working") : t("auth.resetButton")}
            </Button>
            <button type="button" className="text-sm font-semibold text-accent underline" onClick={() => { setError(null); setStep(1); }}>
              {t("auth.resendCode")}
            </button>
          </form>
        )}
        <p className="mt-5 text-sm">
          <Link href="/signin" className="font-semibold text-accent underline">
            {t("auth.backToSignIn")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
