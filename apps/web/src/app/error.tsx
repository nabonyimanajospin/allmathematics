"use client";

import { Button } from "@allmaths/ui";
import { t } from "@/i18n";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <h1 className="text-3xl font-extrabold">{t("errors.serverTitle")}</h1>
      <p className="mt-3 text-muted">{t("auth.errorGeneric")}</p>
      <Button className="mt-8" onClick={reset}>
        {t("errors.retry")}
      </Button>
    </div>
  );
}
