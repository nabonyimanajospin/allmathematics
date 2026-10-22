"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@allmaths/ui";

export function RemoveFormulaButton({ lessonId, sectionId, label }: { lessonId: string; sectionId: string; label: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  return (
    <button
      type="button"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        try {
          await fetch("/api/formulas", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ lessonId, sectionId, saved: false }) });
        } finally {
          setBusy(false);
          router.refresh();
        }
      }}
      className="min-h-9 font-semibold text-danger underline underline-offset-2 disabled:opacity-50"
    >
      {label}
    </button>
  );
}

export function PrintButton({ label }: { label: string }) {
  return (
    <Button variant="secondary" onClick={() => window.print()}>
      {label}
    </Button>
  );
}
