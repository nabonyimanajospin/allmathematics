import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { can, listAnnouncements } from "@allmaths/server";
import { Card } from "@allmaths/ui";
import { AdminNav } from "@/components/admin-nav";
import { AnnouncementActions, NewAnnouncement } from "@/components/announcement-admin";
import { BackLink } from "@/components/back-link";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("admin.announcements.title") };
export const dynamic = "force-dynamic";

const fmt = (d: Date) => d.toISOString().slice(0, 16).replace("T", " ");

export default async function AdminAnnouncementsPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/admin/announcements");
  if (!can(user.role, "users:manage")) notFound();
  const { db } = await getServices();
  const rows = await listAnnouncements(db);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <BackLink href="/admin">{t("admin.nav.overview")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("admin.announcements.title")}</h1>
      <p className="mt-3 mb-6 text-muted">{t("admin.announcements.lead")}</p>
      <AdminNav current="announcements" />
      <Card>
        <NewAnnouncement />
      </Card>
      {rows.length === 0 ? <p className="mt-6 text-muted">{t("admin.announcements.none")}</p> : null}
      <ul className="mt-6 grid gap-3">
        {rows.map((r) => (
          <li key={r.id} className="rounded-[var(--radius)] border border-line bg-surface p-4">
            <p className="text-sm text-muted">
              {fmt(r.createdAt)} · {r.active ? t("admin.announcements.visible") : t("admin.announcements.hidden")}
            </p>
            <p className="mt-1 whitespace-pre-wrap break-words">{r.message}</p>
            <div className="mt-3">
              <AnnouncementActions id={r.id} active={r.active} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
