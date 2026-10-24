import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { can, feedbackCounts, listFeedback } from "@allmaths/server";
import { buttonClass } from "@allmaths/ui";
import { AdminNav } from "@/components/admin-nav";
import { BackLink } from "@/components/back-link";
import { FeedbackActions } from "@/components/feedback-admin";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("admin.feedback.title") };
export const dynamic = "force-dynamic";

const STATUSES = ["new", "read", "resolved"] as const;
const fmt = (d: Date) => d.toISOString().slice(0, 16).replace("T", " ");

export default async function AdminFeedbackPage({ searchParams }: { searchParams: Promise<{ status?: string }> }) {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/admin/feedback");
  if (!can(user.role, "users:manage")) notFound();
  const asked = (await searchParams).status;
  const wanted = STATUSES.find((s) => s === asked);
  const { db } = await getServices();
  const [rows, counts] = await Promise.all([listFeedback(db, wanted ? { status: wanted } : {}), feedbackCounts(db)]);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <BackLink href="/admin">{t("admin.nav.overview")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("admin.feedback.title")}</h1>
      <p className="mt-3 mb-6 text-muted">{t("admin.feedback.lead")}</p>
      <AdminNav current="feedback" />

      <nav aria-label={t("admin.feedback.filter")} className="flex flex-wrap gap-2">
        <Link href="/admin/feedback" className={buttonClass(wanted ? "secondary" : "primary")}>
          {t("admin.feedback.all")} ({counts.new + counts.read + counts.resolved})
        </Link>
        {STATUSES.map((s) => (
          <Link key={s} href={`/admin/feedback?status=${s}`} className={buttonClass(wanted === s ? "primary" : "secondary")}>
            {t(`admin.feedback.status.${s}`)} ({counts[s]})
          </Link>
        ))}
      </nav>

      {rows.length === 0 ? <p className="mt-8 text-muted">{t("admin.feedback.none")}</p> : null}
      <ul className="mt-6 grid gap-4">
        {rows.map((r) => (
          <li key={r.id} className={`rounded-[var(--radius)] border bg-surface p-4 ${r.status === "new" ? "border-2 border-accent" : "border-line"}`}>
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="font-bold">
                {t(`feedback.cat.${r.category}`)} · <span className="text-sm font-semibold text-muted">{t(`admin.feedback.status.${r.status}`)}</span>
              </p>
              <p className="text-sm text-muted">{fmt(r.createdAt)}</p>
            </div>
            <p className="mt-1 text-sm text-muted">
              {r.userName ?? t("admin.feedback.unknownUser")} {r.userEmail ? <span className="break-all">({r.userEmail})</span> : null}
              {r.page ? (
                <>
                  {" · "}
                  <Link href={r.page} className="font-mono text-accent underline">
                    {r.page}
                  </Link>
                </>
              ) : null}
            </p>
            <p className="mt-3 whitespace-pre-wrap break-words">{r.message}</p>
            <div className="mt-4 border-t border-line pt-3">
              <FeedbackActions id={r.id} status={r.status} note={r.adminNote} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
