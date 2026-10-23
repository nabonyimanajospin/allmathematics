import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { getEnrolledCourseId, listCourseCards } from "@allmaths/server";
import { Card } from "@allmaths/ui";
import { BackLink } from "@/components/back-link";
import { EnrollButton } from "@/components/enroll-button";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("courses.title") };
export const dynamic = "force-dynamic";

/** Choose the course to follow. Only one course is open at a time; switching keeps the progress of the others. */
export default async function CoursesPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/signin?next=/courses");
  const { db, store } = await getServices();
  const enrolled = await getEnrolledCourseId(db, user.id);
  const cards = listCourseCards(store);
  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {enrolled ? <BackLink href="/dashboard">{t("lesson.back")}</BackLink> : null}
      <h1 className="text-3xl font-extrabold tracking-tight">{enrolled ? t("courses.switchTitle") : t("courses.title")}</h1>
      <p className="mt-3 max-w-2xl text-muted">{enrolled ? t("courses.switchLead") : t("courses.lead")}</p>
      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {cards.map((c) => (
          <Card key={c.id} className="flex flex-col">
            <h2 className="text-xl font-bold">{c.title}</h2>
            <p className="mt-2 flex-1 text-muted">{c.description}</p>
            <p className="mt-4 text-sm text-muted">{t("courses.facts", { modules: c.modules, lessons: c.lessons, hours: c.hours })}</p>
            <div className="mt-4">
              {c.id === enrolled ? (
                <p className="rounded-full bg-success-soft px-3 py-1 text-center text-sm font-semibold text-success">{t("courses.current")}</p>
              ) : (
                <EnrollButton courseId={c.id} title={c.title} switching={enrolled !== null} />
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
