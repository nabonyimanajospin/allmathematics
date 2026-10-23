import type { Metadata } from "next";
import { BackLink } from "@/components/back-link";
import { Grapher } from "@/components/grapher";
import { t } from "@/i18n";

export const metadata: Metadata = { title: t("grapher.title") };

/** The grapher is open to everyone: it needs no account. */
export default function GraphPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <BackLink href="/">{t("nav.home")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("grapher.title")}</h1>
      <p className="mt-2 mb-6 max-w-3xl text-muted">{t("grapher.lead")}</p>
      <Grapher />
    </div>
  );
}
