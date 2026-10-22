"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@allmaths/ui";
import { t } from "@/i18n";

export function SignOutButton() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  return (
    <Button
      variant="secondary"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        try {
          await fetch("/api/auth/signout", { method: "POST" });
        } finally {
          router.replace("/");
          router.refresh();
        }
      }}
    >
      {t("nav.signOut")}
    </Button>
  );
}
