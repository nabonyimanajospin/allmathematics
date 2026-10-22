import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { toClientLesson } from "@allmaths/content-schema";
import { getCourseOutline, getLessonState } from "@allmaths/server";
import { CourseOutlinePanel } from "@/components/course-outline";
import { t } from "@/i18n";
import { LessonPlayer } from "@/components/lesson/player";
import { renderLesson } from "@/server/render";
import { getServices } from "@/server/runtime";
import { getCurrentUser } from "@/server/session";

type Params = { params: Promise<{ lessonId: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { lessonId } = await params;
  const { store } = await getServices();
  const ref = store.lesson(lessonId);
  return { title: ref?.lesson.title ?? "Lesson" };
}

export default async function LessonPage({ params }: Params) {
  const { lessonId } = await params;
  const user = await getCurrentUser();
  if (!user) redirect(`/signin?next=${encodeURIComponent(`/learn/${lessonId}`)}`);

  const { db, store } = await getServices();
  const ref = store.lesson(lessonId);
  if (!ref) notFound();

  const state = await getLessonState(db, store, user.id, lessonId);
  if (!state) notFound();

  // the next lesson in the course, in curriculum order
  const order = ref.course.modules.flatMap((m) => m.units.flatMap((u) => u.lessons.map((l) => l.meta)));
  const idx = order.findIndex((l) => l.id === lessonId);
  const nextMeta = idx >= 0 ? order[idx + 1] : undefined;

  const outline = await getCourseOutline(db, store, user.id, lessonId);

  const player = (
    <LessonPlayer
      lesson={renderLesson(toClientLesson(ref.lesson))}
      initial={{
        completedSectionIds: state.completedSectionIds,
        solvedExerciseIds: state.solvedExerciseIds,
        hintsUsed: state.hintsUsed,
        resumeSectionId: state.resumeSectionId,
        progress: state.progress,
      }}
      userId={user.id}
      next={nextMeta ? { id: nextMeta.id, title: nextMeta.title } : null}
    />
  );

  if (!outline) return player;
  return (
    <div className="mx-auto max-w-[88rem] lg:grid lg:grid-cols-[22rem_minmax(0,1fr)]">
      <aside className="sticky top-[var(--header-h)] hidden h-[calc(100dvh-var(--header-h))] overflow-y-auto border-r border-line bg-surface lg:block">
        <CourseOutlinePanel outline={outline} />
      </aside>
      <div className="min-w-0">
        <details className="border-b border-line bg-surface lg:hidden">
          <summary className="flex min-h-12 cursor-pointer items-center gap-2 px-4 font-semibold text-accent">{t("outline.open")}</summary>
          <CourseOutlinePanel outline={outline} />
        </details>
        {player}
      </div>
    </div>
  );
}
