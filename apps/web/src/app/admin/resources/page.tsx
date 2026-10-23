import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { can } from "@allmaths/server";
import { buttonClass } from "@allmaths/ui";
import { AdminNav } from "@/components/admin-nav";
import { ResourceUploadForm, RemoveResourceButton } from "@/components/resource-admin";
import { BackLink } from "@/components/back-link";
import { t, type MessageKey } from "@/i18n";
import { getResourceCatalog } from "@/server/resources";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("admin.resources.title") };
export const dynamic = "force-dynamic";

/** Administrators only: upload and remove the documents of the Resources page. */
export default async function AdminResourcesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/admin/resources");
  if (!can(user.role, "resources:manage")) notFound();
  const catalog = getResourceCatalog();
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <BackLink href="/admin">{t("admin.nav.overview")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("admin.resources.title")}</h1>
      <p className="mt-3 mb-6 text-muted">{t("admin.resources.lead")}</p>
      <AdminNav current="resources" />
      <div>
        <ResourceUploadForm />
      </div>

      <h2 className="mt-10 text-xl font-bold">{t("admin.resources.listTitle")}</h2>
      {catalog.resources.length === 0 ? <p className="mt-3 text-muted">{t("admin.resources.none")}</p> : null}
      <ul className="mt-4 divide-y divide-line rounded-[var(--radius)] border border-line bg-surface">
        {catalog.resources.map((r) => (
          <li key={r.id} className="flex items-center justify-between gap-3 p-4">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">
                {t(`resources.kind.${r.kind}` as MessageKey)} · {t(`resources.course.${r.course}` as MessageKey)}
              </p>
              <p className="font-bold">{r.title}</p>
              <p className="text-sm text-muted">{r.file ?? r.id}</p>
            </div>
            <RemoveResourceButton id={r.id} title={r.title} />
          </li>
        ))}
      </ul>
      <p className="mt-6">
        <Link href="/resources" className={buttonClass("secondary")}>
          {t("admin.resources.back")}
        </Link>
      </p>
    </div>
  );
}
