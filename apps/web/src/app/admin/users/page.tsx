import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { can, listUsers } from "@allmaths/server";
import { Button, inputClass } from "@allmaths/ui";
import { AdminNav } from "@/components/admin-nav";
import { UserActions } from "@/components/user-actions";
import { BackLink } from "@/components/back-link";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("admin.users.title") };
export const dynamic = "force-dynamic";

const fmt = (d: Date) => d.toISOString().slice(0, 10);

export default async function AdminUsersPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/admin/users");
  if (!can(user.role, "users:manage")) notFound();
  const q = ((await searchParams).q ?? "").slice(0, 100);
  const { db } = await getServices();
  const rows = await listUsers(db, { q, limit: 50 });
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <BackLink href="/admin">{t("admin.nav.overview")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("admin.users.title")}</h1>
      <p className="mt-3 mb-6 text-muted">{t("admin.users.lead")}</p>
      <AdminNav current="users" />

      <form method="get" className="flex flex-wrap gap-2" role="search">
        <label htmlFor="q" className="sr-only">
          {t("admin.users.search")}
        </label>
        <input id="q" name="q" defaultValue={q} placeholder={t("admin.users.search")} maxLength={100} className={`${inputClass} max-w-sm`} />
        <Button type="submit">{t("admin.users.searchButton")}</Button>
      </form>

      {rows.length === 0 ? <p className="mt-6 text-muted">{t("admin.users.none")}</p> : null}
      <ul className="mt-6 divide-y divide-line rounded-[var(--radius)] border border-line bg-surface">
        {rows.map((r) => (
          <li key={r.id} className="grid gap-3 p-4">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <div className="min-w-0">
                <p className="font-bold">
                  {r.name} {r.id === user.id ? <span className="font-normal text-muted">{t("admin.users.you")}</span> : null}
                </p>
                <p className="break-all text-sm text-muted">{r.email}</p>
              </div>
              <p className="text-sm text-muted">
                {r.role.replace("_", " ")} · {r.suspended ? t("admin.users.suspendedState") : t("admin.users.active")}{r.premium ? ` · ${t("admin.users.premiumBadge")}` : ""} · {t("admin.users.joined")} {fmt(r.createdAt)} ·{" "}
                {t("admin.users.lastSeen")} {r.lastSeenAt ? fmt(r.lastSeenAt) : t("admin.users.never")}
              </p>
            </div>
            <UserActions id={r.id} email={r.email} role={r.role} suspended={r.suspended} premium={r.premium} isSelf={r.id === user.id} />
          </li>
        ))}
      </ul>
      {rows.length > 0 ? <p className="mt-3 text-sm text-muted">{t("admin.users.showing", { n: rows.length })}</p> : null}
    </div>
  );
}
