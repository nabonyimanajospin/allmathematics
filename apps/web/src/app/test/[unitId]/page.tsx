import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { UNIT_TEST_PASS, UNIT_TEST_QUESTIONS, canOpenCourse, getEnrolledCourseId, hasUnitTest, unitTestStatus } from "@allmaths/server";
import { BackLink } from "@/components/back-link";
import { UnitTestRunner } from "@/components/unit-test-runner";
import { t } from "@/i18n";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

export const metadata: Metadata = { title: t("unitTest.title") };
export const dynamic = "force-dynamic";

export default async function UnitTestPage({ params }: { params: Promise<{ unitId: string }> }) {
  const { unitId } = await params;
  const user = await getCurrentUser();
  if (!user) redirect(`/signin?next=${encodeURIComponent(`/test/${unitId}`)}`);
  const { db, store } = await getServices();
  const found = store.courses.flatMap((c) => c.modules.flatMap((m) => m.units.filter((u) => u.meta.id === unitId).map((u) => ({ course: c.meta, module: m.meta, unit: u.meta }))))[0];
  if (!found || !hasUnitTest(store, unitId)) notFound();
  if (!canOpenCourse(user.role, await getEnrolledCourseId(db, user.id), found.course.id)) redirect("/courses");
  const status = await unitTestStatus(db, store, user.id, unitId);
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <BackLink href="/dashboard">{t("lesson.back")}</BackLink>
      <p className="text-sm text-muted">
        {found.course.title} · {found.module.title}
      </p>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("unitTest.heading", { unit: found.unit.title })}</h1>
      <div className="mt-6">
        <UnitTestRunner unitId={unitId} passScore={UNIT_TEST_PASS} questions={UNIT_TEST_QUESTIONS} attempts={status.attempts} bestScore={status.bestScore} passed={status.passed} />
      </div>
    </div>
  );
}
