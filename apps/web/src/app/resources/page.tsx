import type { Metadata } from "next";
import { isDownloadable, type Resource } from "@allmaths/content-schema";
import { Card, buttonClass } from "@allmaths/ui";
import { t, type MessageKey } from "@/i18n";
import { getResourceCatalog } from "@/server/resources";

export const metadata: Metadata = { title: t("resources.title") };
export const dynamic = "force-dynamic";

const COURSES = ["geo", "mvc", "stat"] as const;

export default function ResourcesPage() {
  const catalog = getResourceCatalog();
  const byCourse = COURSES.map((c) => ({ course: c, items: catalog.resources.filter((r) => r.course === c) })).filter((g) => g.items.length > 0);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-3xl font-extrabold tracking-tight">{t("resources.title")}</h1>
      <p className="mt-3 max-w-2xl text-muted">{t("resources.lead")}</p>
      {byCourse.length === 0 ? <p className="mt-8 text-muted">{t("resources.empty")}</p> : null}
      {byCourse.map((g) => (
        <section key={g.course} aria-labelledby={`c-${g.course}`} className="mt-10">
          <h2 id={`c-${g.course}`} className="text-xl font-bold">
            {t(`resources.course.${g.course}` as MessageKey)}
          </h2>
          <ul className="mt-4 grid gap-4 sm:grid-cols-2">
            {g.items.map((r: Resource) => {
              const ok = isDownloadable(catalog, r);
              return (
                <li key={r.id}>
                  <Card>
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted">{t(`resources.kind.${r.kind}` as MessageKey)}</p>
                    <h3 className="mt-1 text-lg font-bold">{r.title}</h3>
                    <p className="mt-2 text-muted">{r.description}</p>
                    <div className="mt-4">
                      {ok ? (
                        <a href={`/resources/download/${r.id}`} download className={buttonClass("primary")}>
                          {t("resources.download")}
                        </a>
                      ) : (
                        <p className="text-sm text-muted">{t("resources.unavailable")}</p>
                      )}
                    </div>
                  </Card>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
