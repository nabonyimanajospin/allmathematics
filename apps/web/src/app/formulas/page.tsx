import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { listFormulas } from "@allmaths/server";
import { t } from "@/i18n";
import { renderInline, renderMath, renderRich } from "@/server/render";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";
import { PrintButton, RemoveFormulaButton } from "./buttons";

export const metadata: Metadata = { title: t("formulas.title") };
export const dynamic = "force-dynamic";

export default async function FormulaSheetPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/formulas");
  const { db, store } = await getServices();
  const saved = await listFormulas(db, store, user.id);

  const groups = new Map<string, { title: string; items: typeof saved }>();
  for (const f of saved) {
    const key = `${f.courseId}|${f.moduleTitle}`;
    const g = groups.get(key) ?? { title: `${f.courseTitle} — ${f.moduleTitle}`, items: [] };
    g.items.push(f);
    groups.set(key, g);
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">{t("formulas.title")}</h1>
          <p className="mt-3 max-w-2xl text-muted">{t("formulas.lead")}</p>
        </div>
        {saved.length > 0 ? (
          <div className="print:hidden">
            <PrintButton label={t("formulas.print")} />
          </div>
        ) : null}
      </div>

      {saved.length === 0 ? (
        <p className="mt-10 rounded-[var(--radius)] border border-line bg-surface-2 p-5 text-muted">{t("formulas.empty")}</p>
      ) : null}

      {[...groups.values()].map((g) => (
        <section key={g.title} className="mt-10 break-inside-avoid">
          <h2 className="text-lg font-bold text-accent">{g.title}</h2>
          <ul className="mt-3 grid gap-4">
            {g.items.map((f) => {
              const ref = store.lesson(f.lessonId);
              const section = ref?.lesson.sections.find((s) => s.id === f.sectionId);
              if (!section) return null;
              const title = section.type === "formula" ? renderInline(section.title) : section.type === "theorem" && section.name ? renderInline(section.name) : "";
              const body =
                section.type === "formula"
                  ? `<div class="text-center text-lg">${renderMath(section.formula, true)}</div>${section.note ? renderRich(section.note) : ""}`
                  : section.type === "theorem"
                    ? renderRich(section.statement)
                    : "";
              return (
                <li key={`${f.lessonId}-${f.sectionId}`} className="rounded-[var(--radius)] border border-line bg-surface p-5">
                  <p className="text-sm font-bold uppercase tracking-wide text-muted">
                    {t(f.kind === "formula" ? "lesson.formula" : "lesson.theorem")}
                    {title ? <>: <span dangerouslySetInnerHTML={{ __html: title }} /></> : null}
                  </p>
                  <div className="rich mt-2" dangerouslySetInnerHTML={{ __html: body }} />
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-sm print:hidden">
                    <Link href={`/learn/${f.lessonId}`} className="font-semibold text-accent underline underline-offset-2">
                      {t("formulas.openLesson", { title: f.lessonTitle })}
                    </Link>
                    <RemoveFormulaButton lessonId={f.lessonId} sectionId={f.sectionId} label={t("formulas.remove")} />
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
