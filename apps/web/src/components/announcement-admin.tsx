"use client";

import { useRouter } from "next/navigation";
import { useId, useState, type FormEvent } from "react";
import { Button, Field, inputClass } from "@allmaths/ui";
import { t } from "@/i18n";

async function call(url: string, body: unknown): Promise<string | null> {
  try {
    const res = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (res.ok) return null;
    const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
    return data?.error?.message ?? t("auth.errorGeneric");
  } catch {
    return t("auth.errorNetwork");
  }
}

export function NewAnnouncement() {
  const uid = useId();
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    const err = await call("/api/admin/announcements", { message });
    setBusy(false);
    setError(err);
    if (!err) {
      setMessage("");
      router.refresh();
    }
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-3">
      <Field label={t("admin.announcements.message")} id={`${uid}-m`} hint={t("admin.announcements.hint")}>
        <textarea id={`${uid}-m`} value={message} onChange={(e) => setMessage(e.target.value)} maxLength={500} rows={3} className={inputClass} />
      </Field>
      {error ? (
        <p role="alert" className="text-danger">
          {error}
        </p>
      ) : null}
      <div>
        <Button type="submit" disabled={busy || message.trim().length < 3}>
          {t("admin.announcements.publish")}
        </Button>
      </div>
    </form>
  );
}

export function AnnouncementActions({ id, active }: { id: string; active: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(action: "show" | "hide" | "delete") {
    if (action === "delete" && !window.confirm(t("admin.announcements.deleteConfirm"))) return;
    setBusy(true);
    const err = await call(`/api/admin/announcements/${id}`, { action });
    setBusy(false);
    setError(err);
    if (!err) router.refresh();
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button variant="secondary" disabled={busy} onClick={() => run(active ? "hide" : "show")}>
        {active ? t("admin.announcements.hide") : t("admin.announcements.show")}
      </Button>
      <Button variant="secondary" disabled={busy} onClick={() => run("delete")}>
        {t("admin.announcements.delete")}
      </Button>
      {error ? (
        <span role="alert" className="text-sm text-danger">
          {error}
        </span>
      ) : null}
    </div>
  );
}
