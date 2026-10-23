import { statSync } from "node:fs";
import { extname, join } from "node:path";
import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { isDownloadable, type Resource } from "@allmaths/content-schema";
import { can } from "@allmaths/server";
import { buttonClass } from "@allmaths/ui";
import { BackLink } from "@/components/back-link";
import { t, type MessageKey } from "@/i18n";
import { getResourceCatalog } from "@/server/resources";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("resources.title") };
export const dynamic = "force-dynamic";

function sizeLabel(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const COURSES = ["geo", "mvc", "stat"] as const;

export default async function ResourcesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/resources");
  const catalog = getResourceCatalog();
  const byCourse = COURSES.map((c) => ({ course: c, items: catalog.resources.filter((r) => r.course === c) })).filter((g) => g.items.length > 0);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("resources.title")}</h1>
      <p className="mt-3 max-w-2xl text-muted">{t("resources.lead")}</p>
      {can(user.role, "resources:manage") ? (
        <p className="mt-4">
          <a href="/admin/resources" className={buttonClass("primary")}>
            {t("resources.manage")}
          </a>
        </p>
      ) : null}

      {byCourse.length > 1 ? (
        <nav aria-label={t("resources.jump")} className="mt-6 flex flex-wrap gap-2">
          {byCourse.map((g) => (
            <a key={g.course} href={`#c-${g.course}`} className={buttonClass("secondary")}>
              {t(`resources.course.${g.course}` as MessageKey)}
            </a>
          ))}
        </nav>
      ) : null}

      {byCourse.length === 0 ? <p className="mt-8 text-muted">{t("resources.empty")}</p> : null}
      {byCourse.map((g) => (
        <section key={g.course} aria-labelledby={`c-${g.course}-h`} id={`c-${g.course}`} className="mt-10 scroll-mt-24">
          <h2 id={`c-${g.course}-h`} className="text-xl font-bold">
            {t(`resources.course.${g.course}` as MessageKey)}
          </h2>
          <div className="mt-4 rounded-[var(--radius)] border border-line bg-surface shadow-[var(--shadow-sm)]">
            <ul className="divide-y divide-line">
              {g.items.map((r: Resource) => {
                const ok = isDownloadable(catalog, r);
                const ext = r.file ? extname(r.file).slice(1).toUpperCase() : "";
                const size = ok && r.file ? sizeLabel(statSync(join(catalog.filesDir, r.file)).size) : "";
                return (
                  <li key={r.id} className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0">
                      <p className="text-xs font-semibold uppercase tracking-wide text-muted">
                        {t(`resources.kind.${r.kind}` as MessageKey)}
                        {ok ? ` · ${ext} · ${size}` : ""}
                      </p>
                      <h3 className="mt-0.5 text-base font-bold">{r.title}</h3>
                      <p className="mt-1 text-sm text-muted">{r.description}</p>
                    </div>
                    <div className="flex shrink-0 flex-wrap items-center gap-2">
                      {ok ? (
                        <>
                          {ext === "PDF" ? (
                            <a href={`/resources/view/${r.id}`} className={buttonClass("secondary")}>
                              {t("resources.preview")}
                            </a>
                          ) : null}
                          <a href={`/resources/download/${r.id}`} download className={buttonClass("primary")}>
                            {t("resources.download")}
                          </a>
                        </>
                      ) : (
                        <p className="text-sm text-muted">{t("resources.unavailable")}</p>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        </section>
      ))}
    </div>
  );
}
