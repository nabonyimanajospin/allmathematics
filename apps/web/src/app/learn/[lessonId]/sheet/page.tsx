import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { toClientLesson } from "@allmaths/content-schema";
import { canOpenCourse, getEnrolledCourseId } from "@allmaths/server";
import { BackLink } from "@/components/back-link";
import { Rich, RichInline } from "@/components/lesson/rich";
import { PrintButton } from "@/app/formulas/buttons";
import { t } from "@/i18n";
import { renderLesson } from "@/server/render";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ lessonId: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { lessonId } = await params;
  const { store } = await getServices();
  return { title: `${t("sheet.title")}: ${store.lesson(lessonId)?.lesson.title ?? ""}` };
}

/**
 * A printable study sheet of one lesson: the objectives, the definitions, theorems and formulas, the worked examples, the summary and all the
 * exercises with room for the working. It contains no answers: those are only checked on the server after the student submits one.
 */
export default async function LessonSheetPage({ params }: Params) {
  const { lessonId } = await params;
  const user = await getCurrentUser();
  if (!user) redirect(`/signin?next=${encodeURIComponent(`/learn/${lessonId}/sheet`)}`);
  const { db, store } = await getServices();
  const ref = store.lesson(lessonId);
  if (!ref) notFound();
  if (!canOpenCourse(user.role, await getEnrolledCourseId(db, user.id), ref.course.meta.id)) redirect("/courses");

  const lesson = renderLesson(toClientLesson(ref.lesson));
  let n = 0;
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 print:max-w-none print:px-0 print:py-0">
      <div className="print:hidden">
        <BackLink href={`/learn/${lessonId}`}>{t("sheet.back")}</BackLink>
        <PrintButton label={t("sheet.print")} />
      </div>

      <header className="mt-4 border-b border-line pb-4">
        <p className="text-sm text-muted">
          {ref.course.meta.title} · {ref.module.meta.title}
        </p>
        <h1 className="text-3xl font-extrabold tracking-tight">{lesson.title}</h1>
        <p className="mt-3 text-sm text-muted">{t("sheet.nameLine")}</p>
      </header>

      {lesson.objectivesHtml.length > 0 ? (
        <section className="mt-6 break-inside-avoid">
          <h2 className="text-xl font-bold">{t("sheet.objectives")}</h2>
          <ul className="mt-2 list-disc pl-6">
            {lesson.objectivesHtml.map((o, i) => (
              <li key={i}>
                <RichInline html={o} />
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="mt-8">
        <h2 className="text-xl font-bold">{t("sheet.keyFacts")}</h2>
        <div className="mt-3 grid gap-4">
          {lesson.sections.map((s) => {
            switch (s.type) {
              case "concept":
                return (
                  <div key={s.id} className="break-inside-avoid">
                    {s.titleHtml ? (
                      <h3 className="font-bold">
                        <RichInline html={s.titleHtml} />
                      </h3>
                    ) : null}
                    <Rich html={s.bodyHtml} />
                  </div>
                );
              case "definition":
                return (
                  <div key={s.id} className="break-inside-avoid rounded-[var(--radius-sm)] border border-line p-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted">{t("lesson.definition")}</p>
                    <h3 className="font-bold">
                      <RichInline html={s.termHtml} />
                    </h3>
                    <Rich html={s.bodyHtml} />
                  </div>
                );
              case "theorem":
                return (
                  <div key={s.id} className="break-inside-avoid rounded-[var(--radius-sm)] border border-line p-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted">{t("lesson.theorem")}</p>
                    {s.nameHtml ? (
                      <h3 className="font-bold">
                        <RichInline html={s.nameHtml} />
                      </h3>
                    ) : null}
                    <Rich html={s.statementHtml} />
                  </div>
                );
              case "formula":
                return (
                  <div key={s.id} className="break-inside-avoid rounded-[var(--radius-sm)] border-2 border-line p-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted">{t("lesson.formula")}</p>
                    <h3 className="font-bold">
                      <RichInline html={s.titleHtml} />
                    </h3>
                    <div dangerouslySetInnerHTML={{ __html: s.formulaHtml }} />
                    {s.noteHtml ? <Rich html={s.noteHtml} className="text-sm" /> : null}
                  </div>
                );
              case "example":
                return (
                  <div key={s.id} className="break-inside-avoid">
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted">{t("lesson.example")}</p>
                    {s.titleHtml ? (
                      <h3 className="font-bold">
                        <RichInline html={s.titleHtml} />
                      </h3>
                    ) : null}
                    <Rich html={s.problemHtml} />
                    <ol className="mt-1 list-decimal pl-6">
                      {s.steps.map((st, i) => (
                        <li key={i}>
                          <Rich html={st.html} />
                        </li>
                      ))}
                    </ol>
                    <Rich html={s.answerHtml} className="font-semibold" />
                  </div>
                );
              case "summary":
                return (
                  <div key={s.id} className="break-inside-avoid">
                    <h3 className="font-bold">{t("lesson.summary")}</h3>
                    <ul className="list-disc pl-6">
                      {s.pointsHtml.map((p, i) => (
                        <li key={i}>
                          <Rich html={p} />
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              default:
                return null; // figures and the quick checks stay in the lesson
            }
          })}
        </div>
        <p className="mt-3 text-sm text-muted print:hidden">{t("sheet.figuresNote")}</p>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold">{t("sheet.practice")}</h2>
        {lesson.exerciseSets.map((set) => (
          <div key={set.id} className="mt-4">
            <h3 className="font-semibold">
              <Rich html={set.taskHtml} />
            </h3>
            <ol className="mt-2 grid gap-4">
              {set.items.map((e) => {
                n += 1;
                return (
                  <li key={e.id} className="break-inside-avoid">
                    <div className="flex gap-2">
                      <span className="font-bold tabular-nums">{n}.</span>
                      <div className="min-w-0 flex-1">
                        <Rich html={e.statementHtml} />
                        {e.choicesHtml ? (
                          <ul className="mt-1 grid gap-1">
                            {e.choicesHtml.map((c, i) => (
                              <li key={i} className="flex gap-2">
                                <span aria-hidden="true">○</span>
                                <RichInline html={c} />
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div className="mt-2 h-14 rounded-[var(--radius-sm)] border border-dashed border-line print:h-20" aria-hidden="true" />
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ol>
          </div>
        ))}
        <p className="mt-6 text-sm text-muted print:hidden">{t("sheet.checkOnline")}</p>
      </section>
    </div>
  );
}
