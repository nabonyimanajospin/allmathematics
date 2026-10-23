import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { BackLink } from "@/components/back-link";
import { Grapher } from "@/components/grapher";
import { t } from "@/i18n";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("grapher.title") };
export const dynamic = "force-dynamic";

/** The grapher is part of the learner's account: sign in first. */
export default async function GraphPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/graph");
  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("grapher.title")}</h1>
      <p className="mt-2 mb-6 max-w-3xl text-muted">{t("grapher.lead")}</p>
      <Grapher />
    </div>
  );
}
