import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { can, getAdminStats } from "@allmaths/server";
import { Card } from "@allmaths/ui";
import { AdminNav } from "@/components/admin-nav";
import { BackLink } from "@/components/back-link";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("admin.overview.title") };
export const dynamic = "force-dynamic";

function Tile({ label, value }: { label: string; value: number }) {
  return (
    <Card className="p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-1 text-3xl font-extrabold tabular-nums">{value}</p>
    </Card>
  );
}

export default async function AdminOverviewPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/admin");
  if (!can(user.role, "users:manage")) notFound();
  const { db } = await getServices();
  const s = await getAdminStats(db);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("admin.overview.title")}</h1>
      <p className="mt-3 mb-6 text-muted">{t("admin.overview.lead")}</p>
      <AdminNav current="overview" />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Tile label={t("admin.overview.totalUsers")} value={s.totalUsers} />
        <Tile label={t("admin.overview.newUsers")} value={s.newLast7Days} />
        <Tile label={t("admin.overview.activeUsers")} value={s.activeLast7Days} />
        <Tile label={t("admin.overview.suspended")} value={s.suspended} />
      </div>

      <h2 className="mt-10 text-xl font-bold">{t("admin.overview.coursesTitle")}</h2>
      <p className="mt-1 text-sm text-muted">{t("admin.overview.enteredHint")}</p>
      {s.courses.length === 0 ? <p className="mt-3 text-muted">{t("admin.overview.noCourses")}</p> : null}
      {s.courses.length > 0 ? (
        <div className="mt-4 overflow-x-auto rounded-[var(--radius)] border border-line bg-surface">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-line text-muted">
              <tr>
                <th scope="col" className="p-3 font-semibold">{t("admin.overview.course")}</th>
                <th scope="col" className="p-3 text-right font-semibold">{t("admin.overview.entered")}</th>
                <th scope="col" className="p-3 text-right font-semibold">{t("admin.overview.completed")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {s.courses.map((c) => (
                <tr key={c.courseId}>
                  <th scope="row" className="p-3 font-semibold">{c.title}</th>
                  <td className="p-3 text-right tabular-nums">{c.entered}</td>
                  <td className="p-3 text-right tabular-nums">{c.completed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      <h2 className="mt-10 text-xl font-bold">{t("admin.overview.byRole")}</h2>
      <ul className="mt-4 flex flex-wrap gap-2">
        {Object.entries(s.byRole).map(([role, n]) => (
          <li key={role} className="rounded-full border border-line bg-surface px-3 py-1 text-sm">
            {role.replace("_", " ")}: <strong className="tabular-nums">{n}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}
