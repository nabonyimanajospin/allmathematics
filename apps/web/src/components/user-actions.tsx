"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@allmaths/ui";
import { t } from "@/i18n";

const ROLES = ["student", "instructor", "content_author", "reviewer", "admin"] as const;

type Action =
  | { action: "reset_password" }
  | { action: "suspend" }
  | { action: "unsuspend" }
  | { action: "set_role"; role: (typeof ROLES)[number] }
  | { action: "grant_premium"; days: number }
  | { action: "revoke_premium" };

export function UserActions({ id, email, role, suspended, premium, isSelf }: { id: string; email: string; role: string; suspended: boolean; premium: boolean; isSelf: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [temporary, setTemporary] = useState<string | null>(null);

  async function run(body: Action, confirmText: string) {
    if (!window.confirm(confirmText)) return;
    setBusy(true);
    setError(null);
    setTemporary(null);
    try {
      const res = await fetch(`/api/admin/users/${id}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
      const data = (await res.json().catch(() => null)) as { temporaryPassword?: string; error?: { message?: string } } | null;
      if (!res.ok) setError(data?.error?.message ?? t("auth.errorGeneric"));
      else {
        if (data?.temporaryPassword) setTemporary(data.temporaryPassword);
        router.refresh();
      }
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <Button variant="secondary" disabled={busy} onClick={() => run({ action: "reset_password" }, t("admin.users.resetConfirm", { email }))}>
          {t("admin.users.resetPassword")}
        </Button>
        {premium ? (
          <Button variant="secondary" disabled={busy} onClick={() => run({ action: "revoke_premium" }, t("admin.users.revokeConfirm", { email }))}>
            {t("admin.users.revokePremium")}
          </Button>
        ) : (
          <select
            aria-label={`${t("admin.users.givePremium")}: ${email}`}
            value=""
            disabled={busy}
            onChange={(e) => {
              const days = Number(e.target.value);
              e.target.value = "";
              if (days > 0) void run({ action: "grant_premium", days }, t("admin.users.grantConfirm", { email, days }));
            }}
            className="rounded-[var(--radius-sm)] border border-line bg-surface px-2 py-2 text-sm"
          >
            <option value="">{t("admin.users.givePremium")}</option>
            <option value="30">30 {t("admin.users.days")}</option>
            <option value="90">90 {t("admin.users.days")}</option>
            <option value="365">365 {t("admin.users.days")}</option>
          </select>
        )}
        {!isSelf ? (
          <>
            <Button
              variant="secondary"
              disabled={busy}
              onClick={() => run({ action: suspended ? "unsuspend" : "suspend" }, t("admin.users.suspendConfirm", { email }))}
            >
              {suspended ? t("admin.users.unsuspend") : t("admin.users.suspend")}
            </Button>
            <select
              aria-label={`${t("admin.users.changeRole")}: ${email}`}
              value={role}
              disabled={busy}
              onChange={(e) => {
                const next = e.target.value as (typeof ROLES)[number];
                void run({ action: "set_role", role: next }, t("admin.users.roleConfirm", { email, role: next.replace("_", " ") }));
                e.target.value = role;
              }}
              className="rounded-[var(--radius-sm)] border border-line bg-surface px-2 py-2 text-sm"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r.replace("_", " ")}
                </option>
              ))}
            </select>
          </>
        ) : null}
      </div>
      {temporary ? (
        <div role="status" className="rounded-[var(--radius-sm)] bg-success-soft px-3 py-2 text-sm">
          <p className="font-semibold">{t("admin.users.tempTitle", { email })}</p>
          <p className="mt-1 select-all font-mono text-base font-bold">{temporary}</p>
          <p className="mt-1 text-muted">{t("admin.users.tempLead")}</p>
        </div>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}
