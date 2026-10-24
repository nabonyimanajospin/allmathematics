import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { can, listAudit } from "@allmaths/server";
import { AdminNav } from "@/components/admin-nav";
import { BackLink } from "@/components/back-link";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("admin.audit.title") };
export const dynamic = "force-dynamic";

const fmt = (d: Date) => d.toISOString().slice(0, 16).replace("T", " ");

/** Everything an administrator did (password resets, suspensions, uploads, feedback decisions), newest first. */
export default async function AdminAuditPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/admin/audit");
  if (!can(user.role, "users:manage")) notFound();
  const { db } = await getServices();
  const rows = await listAudit(db, 200);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <BackLink href="/admin">{t("admin.nav.overview")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("admin.audit.title")}</h1>
      <p className="mt-3 mb-6 text-muted">{t("admin.audit.lead")}</p>
      <AdminNav current="audit" />
      {rows.length === 0 ? <p className="text-muted">{t("admin.audit.none")}</p> : null}
      {rows.length > 0 ? (
        <div className="overflow-x-auto rounded-[var(--radius)] border border-line bg-surface">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-line text-muted">
              <tr>
                <th scope="col" className="p-3 font-semibold">{t("admin.audit.when")}</th>
                <th scope="col" className="p-3 font-semibold">{t("admin.audit.who")}</th>
                <th scope="col" className="p-3 font-semibold">{t("admin.audit.action")}</th>
                <th scope="col" className="p-3 font-semibold">{t("admin.audit.target")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {rows.map((r) => (
                <tr key={r.id}>
                  <td className="whitespace-nowrap p-3 tabular-nums">{fmt(r.at)}</td>
                  <td className="p-3 break-all">{r.actorEmail ?? "—"}</td>
                  <td className="p-3 font-mono">{r.action}</td>
                  <td className="p-3 font-mono break-all text-muted">{r.target ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
