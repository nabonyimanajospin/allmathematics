"use client";

import { useRouter } from "next/navigation";
import { useId, useState, type FormEvent } from "react";
import { Button, Card, Field, inputClass } from "@allmaths/ui";
import { t, type MessageKey } from "@/i18n";

const KINDS = ["book", "notes", "exercises", "formulas", "syllabus"] as const;
const COURSES = ["geo", "mvc", "stat"] as const;

async function errorMessage(res: Response): Promise<string> {
  const body = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
  return body?.error?.message ?? t("auth.errorGeneric");
}

export function ResourceUploadForm() {
  const router = useRouter();
  const uid = useId();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    setError(null);
    setDone(false);
    setBusy(true);
    try {
      const res = await fetch("/api/admin/resources", { method: "POST", body: new FormData(form) });
      if (res.ok) {
        form.reset();
        setDone(true);
        router.refresh();
      } else {
        setError(await errorMessage(res));
      }
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold">{t("admin.resources.uploadTitle")}</h2>
      <form onSubmit={onSubmit} className="mt-4 grid gap-4">
        <Field label={t("admin.resources.file")} id={`${uid}-file`} hint={t("admin.resources.fileHint")}>
          <input id={`${uid}-file`} name="file" type="file" required accept=".pdf,.docx,.png,.jpg" className={inputClass} />
        </Field>
        <Field label={t("admin.resources.docTitle")} id={`${uid}-title`}>
          <input id={`${uid}-title`} name="title" required minLength={3} maxLength={160} className={inputClass} />
        </Field>
        <Field label={t("admin.resources.docId")} id={`${uid}-id`} hint={t("admin.resources.docIdHint")}>
          <input id={`${uid}-id`} name="id" required pattern="[a-z0-9]+(-[a-z0-9]+)*" maxLength={80} className={inputClass} />
        </Field>
        <Field label={t("admin.resources.description")} id={`${uid}-description`}>
          <textarea id={`${uid}-description`} name="description" required minLength={3} maxLength={400} rows={3} className={inputClass} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label={t("admin.resources.kind")} id={`${uid}-kind`}>
            <select id={`${uid}-kind`} name="kind" required className={inputClass}>
              {KINDS.map((k) => (
                <option key={k} value={k}>
                  {t(`resources.kind.${k}` as MessageKey)}
                </option>
              ))}
            </select>
          </Field>
          <Field label={t("admin.resources.course")} id={`${uid}-course`}>
            <select id={`${uid}-course`} name="course" required className={inputClass}>
              {COURSES.map((c) => (
                <option key={c} value={c}>
                  {t(`resources.course.${c}` as MessageKey)}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <label className="flex items-start gap-2 text-sm">
          <input type="checkbox" name="confirm" value="yes" required className="mt-1" />
          <span>{t("admin.resources.confirm")}</span>
        </label>
        {error ? (
          <p role="alert" className="rounded-[var(--radius-sm)] bg-danger-soft px-3 py-2 text-sm font-medium text-danger">
            {error}
          </p>
        ) : null}
        {done ? (
          <p role="status" className="text-sm font-medium text-success">
            {t("admin.resources.uploaded")}
          </p>
        ) : null}
        <Button type="submit" disabled={busy}>
          {busy ? t("admin.resources.uploading") : t("admin.resources.upload")}
        </Button>
      </form>
    </Card>
  );
}

export function RemoveResourceButton({ id, title }: { id: string; title: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  return (
    <div className="flex flex-col items-end gap-1">
      <Button
        variant="secondary"
        disabled={busy}
        onClick={async () => {
          if (!window.confirm(t("admin.resources.removeConfirm", { title }))) return;
          setBusy(true);
          setError(null);
          try {
            const res = await fetch(`/api/admin/resources/${id}`, { method: "DELETE" });
            if (res.ok) router.refresh();
            else setError(await errorMessage(res));
          } catch {
            setError(t("auth.errorNetwork"));
          } finally {
            setBusy(false);
          }
        }}
      >
        {t("admin.resources.remove")}
      </Button>
      {error ? (
        <p role="alert" className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}
