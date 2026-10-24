"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";

/** The actions of an administrator on one message: mark it read or resolved, keep a private note, delete it. */
export function FeedbackActions({ id, status, note }: { id: string; status: "new" | "read" | "resolved"; note: string | null }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [text, setText] = useState(note ?? "");
  const [error, setError] = useState<string | null>(null);

  async function run(body: unknown, confirmText?: string) {
    if (confirmText && !window.confirm(confirmText)) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`/api/admin/feedback/${id}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
      const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
      if (!res.ok) setError(data?.error?.message ?? t("auth.errorGeneric"));
      else router.refresh();
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-2">
      <label className="grid gap-1 text-sm font-semibold">
        {t("admin.feedback.note")}
        <textarea value={text} onChange={(e) => setText(e.target.value)} maxLength={1000} rows={2} className={`${inputClass} font-normal`} />
      </label>
      <div className="flex flex-wrap gap-2">
        {status !== "read" ? (
          <Button variant="secondary" disabled={busy} onClick={() => run({ action: "set_status", status: "read", note: text })}>
            {t("admin.feedback.markRead")}
          </Button>
        ) : null}
        {status !== "resolved" ? (
          <Button disabled={busy} onClick={() => run({ action: "set_status", status: "resolved", note: text })}>
            {t("admin.feedback.markResolved")}
          </Button>
        ) : null}
        {status !== "new" ? (
          <Button variant="secondary" disabled={busy} onClick={() => run({ action: "set_status", status: "new", note: text })}>
            {t("admin.feedback.markNew")}
          </Button>
        ) : null}
        {text !== (note ?? "") ? (
          <Button variant="secondary" disabled={busy} onClick={() => run({ action: "set_status", status, note: text })}>
            {t("admin.feedback.saveNote")}
          </Button>
        ) : null}
        <Button variant="secondary" disabled={busy} onClick={() => run({ action: "delete" }, t("admin.feedback.deleteConfirm"))}>
          {t("admin.feedback.delete")}
        </Button>
      </div>
      {error ? (
        <p role="alert" className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}
