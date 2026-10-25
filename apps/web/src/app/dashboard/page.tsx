import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { getDashboard, getEnrolledCourseId } from "@allmaths/server";
import { Card, ProgressBar, ProgressRing, buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("dashboard.title") };

/** Small real progress is shown with a decimal (0.1%), never as 0%; 100% only when everything is done. */
function shown(percent: number, tenths: number): string {
  if (percent >= 10 || tenths === 0) return `${percent}%`;
  return `${tenths}%`;
}

function status(percent: number): string {
  return percent >= 100 ? t("dashboard.complete") : percent > 0 ? t("dashboard.inProgress") : t("dashboard.notStarted");
}

export default async function DashboardPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/dashboard");
  const { db, store } = await getServices();
  const enrolled = await getEnrolledCourseId(db, user.id);
  if (!enrolled) redirect("/courses");
  const dash = await getDashboard(db, store, user.id, enrolled);

  const allLessons = dash.courses.flatMap((c) => c.modules.flatMap((m) => m.units.flatMap((u) => u.lessons)));
  const next = allLessons.find((l) => l.id === dash.continueLessonId);
  const firstCourse = dash.courses[0];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-extrabold tracking-tight">{t("dashboard.hello", { name: user.name.split(" ")[0] ?? user.name })}</h1>

      <section aria-labelledby="continue" className="mt-6">
        <Card className="flex flex-wrap items-center gap-5">
          {firstCourse ? (
            <ProgressRing percent={firstCourse.percent} label={t("dashboard.courseProgress")} size={96} tone="success">
              <span className="block text-base leading-tight">{shown(firstCourse.percent, firstCourse.tenths)}</span>
            </ProgressRing>
          ) : null}
          <div className="min-w-[13rem] flex-1">
            <h2 id="continue" className="text-sm font-semibold uppercase tracking-wide text-muted">
              {t("dashboard.continueFrom")}
            </h2>
            {next ? (
              <>
                <p className="mt-1 text-xl font-bold">{next.title}</p>
                <p className="text-sm text-muted">{t("dashboard.minutes", { n: next.estMinutes })}</p>
              </>
            ) : (
              <p className="mt-1 text-lg font-semibold">{t("dashboard.allDone")}</p>
            )}
          </div>
          {next ? (
            <Link href={`/learn/${next.id}`} className={buttonClass("primary", "w-full px-6 sm:w-auto")}>
              {next.percent > 0 ? t("dashboard.resume") : t("dashboard.startLesson")}
            </Link>
          ) : null}
        </Card>
      </section>

      <nav aria-label={t("dashboard.more")} className="mt-4 flex flex-wrap gap-2">
        <Link href="/courses" className={buttonClass("secondary")}>
          {t("courses.switch")}
        </Link>
        {/* the header already has these links from the medium screen up; a phone has no room for them there */}
        <Link href="/formulas" className={buttonClass("secondary", "sm:hidden")}>
          {t("nav.formulas")}
        </Link>
        <Link href="/graph" className={buttonClass("secondary", "md:hidden")}>
          {t("nav.grapher")}
        </Link>
        <Link href="/solver" className={buttonClass("secondary", "md:hidden")}>
          {t("nav.solver")}
        </Link>
      </nav>

      {dash.courses.map((course) => (
        <section key={course.id} aria-labelledby={`course-${course.id}`} className="mt-10">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 id={`course-${course.id}`} className="text-2xl font-bold tracking-tight">
                {course.title}
              </h2>
              <p className="mt-1 max-w-2xl text-muted">{course.description}</p>
            </div>
            <span className="shrink-0 text-lg font-bold tabular-nums text-success">{shown(course.percent, course.tenths)}</span>
          </div>
          <ProgressBar fractional percent={course.tenths} label={`${course.title}: ${t("dashboard.courseProgress")}`} className="mt-3" />

          <div className="mt-5 grid gap-4">
            {course.modules.map((m) => (
              <Card key={m.id} className="p-0">
                <details open={m.percent < 100} className="group">
                  <summary className="flex min-h-14 list-none items-center justify-between gap-3 px-5 py-3 [&::-webkit-details-marker]:hidden">
                    <svg className="size-4 shrink-0 text-muted transition-transform group-open:rotate-90" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M9 5l7 7-7 7" />
                    </svg>
                    <span className="min-w-0 flex-1 font-bold">
                      {t("dashboard.module")} {m.id.slice(-2).replace(/^0/, "")}: {m.title}
                      {m.free ? (
                        <span className="ml-2 rounded-full bg-success-soft px-2 py-0.5 align-middle text-xs font-semibold text-success">
                          {t("dashboard.free")}
                        </span>
                      ) : null}
                    </span>
                    <span className="text-sm font-semibold tabular-nums text-muted">{shown(m.percent, m.tenths)}</span>
                  </summary>
                  <div className="border-t border-line px-5 pb-4">
                    {m.units.map((u) => (
                      <div key={u.id} className="pt-4">
                        <div className="flex items-center justify-between gap-3">
                          <h3 className="font-semibold">
                            {t("dashboard.unit")} {u.id.slice(-2).replace(/^0/, "")}: {u.title}
                          </h3>
                          <span className="text-sm tabular-nums text-muted">{shown(u.percent, u.tenths)}</span>
                        </div>
                        <ProgressBar fractional percent={u.tenths} label={u.title} className="mt-1.5 h-1.5" />
                        <ul className="mt-2 grid gap-1">
                          {u.lessons.map((l) => (
                            <li key={l.id}>
                              <Link
                                href={`/learn/${l.id}`}
                                className="flex min-h-12 items-center justify-between gap-3 rounded-[var(--radius-sm)] px-3 py-2 hover:bg-surface-2"
                              >
                                <span className="min-w-0">
                                  <span className="block font-medium">{l.title}</span>
                                  <span className="block text-sm text-muted">
                                    {t("dashboard.minutes", { n: l.estMinutes })} · {status(l.percent)}
                                  </span>
                                </span>
                                <span
                                  className={`shrink-0 rounded-full px-2.5 py-1 text-sm font-semibold tabular-nums ${
                                    l.percent >= 100 ? "bg-success-soft text-success" : "bg-surface-2 text-ink"
                                  }`}
                                >
                                  {shown(l.percent, l.tenths)}
                                </span>
                              </Link>
                            </li>
                          ))}
                        </ul>
                        {u.test.exists ? (
                          <Link
                            href={`/test/${u.id}`}
                            className="mt-1 flex min-h-12 items-center justify-between gap-3 rounded-[var(--radius-sm)] border border-line px-3 py-2 hover:bg-surface-2"
                          >
                            <span className="min-w-0">
                              <span className="block font-medium">{t("unitTest.open")}</span>
                              <span className="block text-sm text-muted">
                                {u.test.attempts === 0 ? t("unitTest.notTaken") : t("unitTest.best", { best: u.test.bestScore ?? 0, n: 10 })}
                              </span>
                            </span>
                            <span
                              className={`shrink-0 rounded-full px-2.5 py-1 text-sm font-semibold ${u.test.passed ? "bg-success-soft text-success" : "bg-surface-2 text-ink"}`}
                            >
                              {u.test.passed ? t("unitTest.passedBadge") : t("unitTest.take")}
                            </span>
                          </Link>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </details>
              </Card>
            ))}
          </div>
        </section>
      ))}
      <p className="mt-10 text-sm">
        <Link href="/how-progress-works" className="font-semibold text-accent hover:underline">
          {t("progressHelp.link")}
        </Link>
      </p>
    </div>
  );
}
