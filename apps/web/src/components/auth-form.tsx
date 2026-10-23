"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useState, type FormEvent } from "react";
import { Button, Card, Field, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";

type Mode = "signin" | "signup";

export function AuthForm({ mode, next, notice }: { mode: Mode; next: string; notice?: string }) {
  const router = useRouter();
  const uid = useId();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const signup = mode === "signup";

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    const form = new FormData(e.currentTarget);
    const payload = signup
      ? { name: String(form.get("name") ?? ""), email: String(form.get("email") ?? ""), password: String(form.get("password") ?? "") }
      : { email: String(form.get("email") ?? ""), password: String(form.get("password") ?? "") };
    try {
      const res = await fetch(signup ? "/api/auth/signup" : "/api/auth/signin", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        router.replace(next);
        router.refresh();
        return;
      }
      const body = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
      setError(body?.error?.message ?? t("auth.errorGeneric"));
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-10">
      <Card className="p-6 sm:p-8">
        <h1 className="text-2xl font-bold tracking-tight">{signup ? t("auth.signUpTitle") : t("auth.signInTitle")}</h1>
        {notice ? (
          <p role="status" className="mt-4 rounded-[var(--radius-sm)] bg-success-soft px-3 py-2 text-sm font-medium text-success">
            {notice}
          </p>
        ) : null}
        <form onSubmit={onSubmit} className="mt-6 grid gap-4" noValidate={false}>
          {signup ? (
            <Field label={t("auth.name")} id={`${uid}-name`}>
              <input id={`${uid}-name`} name="name" required maxLength={80} autoComplete="name" className={inputClass} />
            </Field>
          ) : null}
          <Field label={t("auth.email")} id={`${uid}-email`}>
            <input id={`${uid}-email`} name="email" type="email" required maxLength={254} autoComplete="email" inputMode="email" className={inputClass} />
          </Field>
          <Field label={t("auth.password")} id={`${uid}-password`} hint={signup ? t("auth.passwordHint") : undefined}>
            <input
              id={`${uid}-password`}
              name="password"
              type="password"
              required
              minLength={signup ? 10 : 1}
              maxLength={128}
              autoComplete={signup ? "new-password" : "current-password"}
              className={inputClass}
            />
          </Field>
          {!signup ? (
            <Link href="/forgot-password" className="text-sm font-semibold text-accent underline">
              {t("auth.forgot")}
            </Link>
          ) : null}
          {error ? (
            <p role="alert" className="rounded-[var(--radius-sm)] bg-danger-soft px-3 py-2 text-sm font-medium text-danger">
              {error}
            </p>
          ) : null}
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? t("auth.working") : signup ? t("auth.signUpButton") : t("auth.signInButton")}
          </Button>
        </form>
        <p className="mt-5 text-sm text-muted">
          {signup ? t("auth.haveAccount") : t("auth.noAccount")}{" "}
          <Link href={`${signup ? "/signin" : "/signup"}?next=${encodeURIComponent(next)}`} className="font-semibold text-accent underline">
            {signup ? t("nav.signIn") : t("nav.signUp")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
