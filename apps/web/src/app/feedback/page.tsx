import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { BackLink } from "@/components/back-link";
import { FeedbackForm } from "@/components/feedback-form";
import { t } from "@/i18n";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("feedback.title") };
export const dynamic = "force-dynamic";

/** Learners tell the administrators about a problem, an idea, a question or a mistake in a lesson. */
export default async function FeedbackPage({ searchParams }: { searchParams: Promise<{ page?: string }> }) {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/feedback");
  const raw = (await searchParams).page ?? "";
  const page = /^\/[A-Za-z0-9\-_/.]{0,198}$/.test(raw) && !raw.startsWith("/feedback") ? raw : null;
  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("feedback.title")}</h1>
      <p className="mt-2 mb-6 text-muted">{t("feedback.lead")}</p>
      <FeedbackForm page={page} />
    </div>
  );
}
