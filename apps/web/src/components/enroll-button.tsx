"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@allmaths/ui";
import { t } from "@/i18n";

export function EnrollButton({ courseId, title, switching }: { courseId: string; title: string; switching: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  return (
    <div>
      <Button
        variant={switching ? "secondary" : "primary"}
        disabled={busy}
        onClick={async () => {
          if (switching && !window.confirm(t("courses.switchConfirm", { title }))) return;
          setBusy(true);
          setError(null);
          try {
            const res = await fetch("/api/enrollment", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ courseId }) });
            if (res.ok) {
              router.push("/dashboard");
              router.refresh();
              return;
            }
            const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
            setError(data?.error?.message ?? t("auth.errorGeneric"));
          } catch {
            setError(t("auth.errorNetwork"));
          }
          setBusy(false);
        }}
      >
        {busy ? t("auth.working") : switching ? t("courses.switchTo") : t("courses.enroll")}
      </Button>
      {error ? (
        <p role="alert" className="mt-2 text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}
