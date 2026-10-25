import type { Metadata } from "next";
import { DEFAULT_MIN_SECONDS, LESSON_WEIGHTS, UNIT_WEIGHTS, lessonProgress, rational } from "@allmaths/core";
import { Card } from "@allmaths/ui";
import { BackLink } from "@/components/back-link";
import { t } from "@/i18n";

export const metadata: Metadata = { title: t("progressHelp.title") };

/** The page shows numbers taken from the very functions that compute progress, so it can never disagree with them. */
export default function HowProgressWorksPage() {
  const seconds = Object.values(DEFAULT_MIN_SECONDS);
  const total = LESSON_WEIGHTS.sections + LESSON_WEIGHTS.practice;
  const example = lessonProgress({
    sectionsCompleted: 8,
    sectionsTotal: 10,
    practiceSolved: 15,
    practiceTotal: 20,
    quizPassed: false,
    hasPractice: true,
    hasQuiz: false,
  });
  const blocks: { title: string; text: string }[] = [
    {
      title: t("progressHelp.lessonTitle"),
      text: t("progressHelp.lessonText", {
        s: LESSON_WEIGHTS.sections,
        p: LESSON_WEIGHTS.practice,
        total,
        sp: `${Math.round((LESSON_WEIGHTS.sections / total) * 100)}%`,
        pp: `${Math.round((LESSON_WEIGHTS.practice / total) * 100)}%`,
      }),
    },
    { title: t("progressHelp.sectionsTitle"), text: t("progressHelp.sectionsText", { min: Math.min(...seconds), max: Math.max(...seconds) }) },
    { title: t("progressHelp.exercisesTitle"), text: t("progressHelp.exercisesText") },
    { title: t("progressHelp.unitTitle"), text: t("progressHelp.unitText", { ul: UNIT_WEIGHTS.lessons, ut: UNIT_WEIGHTS.test }) },
    {
      title: t("progressHelp.exampleTitle"),
      text: t("progressHelp.exampleText", {
        s: LESSON_WEIGHTS.sections,
        p: LESSON_WEIGHTS.practice,
        total,
        num: String(example.num),
        den: String(example.den),
        percent: rational.percentFloor(example),
      }),
    },
    { title: t("progressHelp.changeTitle"), text: t("progressHelp.changeText") },
  ];
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <BackLink href="/dashboard">{t("progressHelp.back")}</BackLink>
      <h1 className="text-3xl font-extrabold tracking-tight">{t("progressHelp.title")}</h1>
      <p className="mt-3 text-muted">{t("progressHelp.lead")}</p>
      <div className="mt-8 grid gap-4">
        {blocks.map((b) => (
          <Card key={b.title}>
            <h2 className="text-lg font-bold">{b.title}</h2>
            <p className="mt-2">{b.text}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
