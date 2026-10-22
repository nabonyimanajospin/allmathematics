"use client";

import type { LessonStateDto, RExerciseSet } from "@/lib/lesson-types";
import { t } from "@/i18n";
import { CheckBlock } from "./check-block";
import { Rich } from "./rich";

interface Props {
  lessonId: string;
  sets: RExerciseSet[];
  solved: ReadonlySet<string>;
  hintsUsed: Record<string, number>;
  onSolved: (exerciseId: string, progress: LessonStateDto["progress"] | undefined) => void;
}

/**
 * The practice area of a lesson. Exercises never block reading: they are optional, every one has hints and a
 * worked solution, and solving them moves the lesson progress (up to 10 solved, spec section 9.2).
 */
export function ExerciseSets({ lessonId, sets, solved, hintsUsed, onSolved }: Props) {
  const total = sets.reduce((n, s) => n + s.items.length, 0);
  const done = sets.reduce((n, s) => n + s.items.filter((i) => solved.has(i.id)).length, 0);
  let counter = 0;
  return (
    <section id="exercises" aria-labelledby="exercises-title" className="mt-14 scroll-mt-32">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <h2 id="exercises-title" className="text-2xl font-bold tracking-tight">
          {t("lesson.exercises")}
        </h2>
        <p className="text-sm font-semibold tabular-nums text-muted" aria-live="polite">
          {t("lesson.exercisesSolved", { solved: done, total })}
        </p>
      </div>
      <p className="mt-1 text-muted">{t("lesson.exercisesLead")}</p>

      <div className="mt-6 grid grid-cols-[minmax(0,1fr)] gap-10">
        {sets.map((set) => (
          <div key={set.id}>
            <Rich html={set.taskHtml} className="font-semibold" />
            {set.formatHtml ? (
              <details className="mt-2 text-sm">
                <summary className="inline-flex min-h-10 items-center font-semibold text-accent">{t("lesson.howToType")}</summary>
                <Rich html={set.formatHtml} className="mt-1 text-muted" />
              </details>
            ) : null}
            <ol className="mt-4 grid grid-cols-[minmax(0,1fr)] gap-5">
              {set.items.map((item) => {
                counter += 1;
                return (
                  <li key={item.id} id={`ex-${item.id}`} className="scroll-mt-32">
                    <p className="mb-1.5 text-sm font-bold uppercase tracking-wide text-accent">
                      {t("lesson.exerciseNumber", { n: counter })}
                    </p>
                    {item.noteHtml ? (
                      <div className="mb-2 rounded-[var(--radius-sm)] bg-warning-soft px-3 py-2 text-sm">
                        <span className="font-bold">{t("lesson.practiceNote")}: </span>
                        <Rich html={item.noteHtml} className="inline" />
                      </div>
                    ) : null}
                    <CheckBlock
                      lessonId={lessonId}
                      compact
                      explanationLabel={t("check.solution")}
                      section={{
                        id: item.id,
                        promptHtml: item.statementHtml,
                        answerType: item.answerType,
                        choicesHtml: item.choicesHtml,
                        hintCount: item.hintCount,
                      }}
                      completed={solved.has(item.id)}
                      hintsUsed={hintsUsed[item.id] ?? 0}
                      onCorrect={(progress) => onSolved(item.id, progress)}
                    />
                  </li>
                );
              })}
            </ol>
          </div>
        ))}
      </div>
    </section>
  );
}
