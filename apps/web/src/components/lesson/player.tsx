"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { lessonProgress, rational, type EventInput } from "@allmaths/core";
import { Card, ProgressBar, buttonClass } from "@allmaths/ui";
import type { LessonStateDto, RLesson } from "@/lib/lesson-types";
import { ActivityTracker, EventQueue, deviceKind, queueKey, type SendResult } from "@/lib/tracker";
import { t } from "@/i18n";
import { CheckBlock } from "./check-block";
import {
  ConceptBlock,
  DefinitionBlock,
  ExampleBlock,
  FormulaBlock,
  SummaryBlock,
  TheoremBlock,
  VisualBlock,
} from "./blocks";
import { ExerciseSets } from "./exercises";
import { Rich, RichInline } from "./rich";

interface Props {
  lesson: RLesson;
  initial: LessonStateDto;
  userId: string;
  /** Formulas and theorems of this lesson that the student saved. */
  savedFormulas: string[];
  next: { id: string; title: string } | null;
}

const FLUSH_EVERY_MS = 5000;
const TICK_MS = 1000;
/** Extra seconds required before the browser shows a section as done, to absorb network delay. */
const OPTIMISTIC_MARGIN_MS = 1500;

const uuid = (): string =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx".replace(/[x]/g, () => Math.floor(Math.random() * 16).toString(16));

function localPercent(done: number, total: number, solved: number, hasPractice: boolean): number {
  return rational.percentFloor(
    lessonProgress({
      sectionsCompleted: Math.min(done, total),
      sectionsTotal: total,
      practiceSolved: solved,
      quizPassed: false,
      hasPractice,
      hasQuiz: false,
    }),
  );
}

export function LessonPlayer({ lesson, initial, userId, savedFormulas, next }: Props) {
  const total = lesson.sections.length;
  const ids = useMemo(() => new Set(lesson.sections.map((s) => s.id)), [lesson]);

  const [completed, setCompleted] = useState<Set<string>>(() => new Set(initial.completedSectionIds));
  const [solved, setSolved] = useState<Set<string>>(() => new Set(initial.solvedExerciseIds));
  const [optimistic, setOptimistic] = useState<Set<string>>(() => new Set());
  const [serverProgress, setServerProgress] = useState(initial.progress);
  const [bookmarked, setBookmarked] = useState<Set<string>>(() => new Set(savedFormulas));
  const [sessionExpired, setSessionExpired] = useState(false);
  const [showResume, setShowResume] = useState(
    initial.progress.lesson.percent > 0 && initial.progress.lesson.percent < 100,
  );

  const trackerRef = useRef<ActivityTracker | null>(null);
  const queueRef = useRef<EventQueue | null>(null);
  const margins = useRef(new Map<string, number>());
  const optimisticRef = useRef(optimistic);
  optimisticRef.current = optimistic;
  const completedRef = useRef(completed);
  completedRef.current = completed;

  const applyServerState = useCallback(
    (state: LessonStateDto) => {
      const done = new Set(state.completedSectionIds.filter((id) => ids.has(id)));
      setCompleted(done);
      setSolved(new Set(state.solvedExerciseIds));
      setServerProgress(state.progress);
      setOptimistic((prev) => {
        const out = new Set<string>();
        for (const id of prev) if (!done.has(id)) out.add(id);
        return out;
      });
    },
    [ids],
  );

  // --- telemetry: tracker, queue, observers -----------------------------------------------------------
  useEffect(() => {
    const now = () => Date.now();
    const tracker = new ActivityTracker(now());
    let storage: Storage | null = null;
    try {
      storage = window.localStorage;
    } catch {
      storage = null;
    }

    const send = async (batch: EventInput[]): Promise<SendResult> => {
      try {
        const res = await fetch("/api/events", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ events: batch }),
          keepalive: true,
        });
        if (res.ok) {
          setSessionExpired(false);
          const data = (await res.json()) as { states?: Record<string, LessonStateDto> };
          const state = data.states?.[lesson.id];
          if (state) {
            // sections whose time was just reported but which the server does not count yet need more time
            const reported = new Set(batch.map((e) => e.sectionId).filter((x): x is string => !!x));
            for (const id of optimisticRef.current) {
              if (reported.has(id) && !state.completedSectionIds.includes(id)) {
                margins.current.set(id, (margins.current.get(id) ?? OPTIMISTIC_MARGIN_MS) + 5000);
              }
            }
            applyServerState(state);
          }
          return "ok";
        }
        if (res.status === 401) {
          setSessionExpired(true);
          return "retry";
        }
        return res.status === 400 || res.status === 413 ? "drop" : "retry";
      } catch {
        return "retry";
      }
    };

    const queue = new EventQueue(queueKey(userId), storage, send);
    trackerRef.current = tracker;
    queueRef.current = queue;

    const event = (verb: EventInput["verb"], sectionId?: string, durationMs?: number): EventInput => ({
      eventId: uuid(),
      verb,
      lessonId: lesson.id,
      ...(sectionId ? { sectionId } : {}),
      ...(durationMs !== undefined ? { result: { durationMs } } : {}),
      clientTimestamp: now(),
      device: deviceKind(window.innerWidth),
    });

    const drainToQueue = () => {
      tracker.tick(now());
      for (const [sectionId, ms] of tracker.drain()) {
        const rounded = Math.round(ms);
        if (rounded > 0) queue.push(event("viewed", sectionId, rounded));
      }
    };

    // Of the sections on screen, the one nearest the middle of the viewport is the one being read.
    const els = Array.from(document.querySelectorAll<HTMLElement>("[data-section]"));
    const visibleNow = new Set<string>();
    const pick = () => {
      const mid = window.innerHeight / 2;
      let best: string | null = null;
      let bestDist = Infinity;
      for (const el of els) {
        const id = el.dataset.section;
        if (!id || !visibleNow.has(id)) continue;
        const r = el.getBoundingClientRect();
        const dist = r.top <= mid && r.bottom >= mid ? 0 : Math.min(Math.abs(r.top - mid), Math.abs(r.bottom - mid));
        if (dist < bestDist) {
          best = id;
          bestDist = dist;
        }
      }
      if (best && tracker.enter(best, now())) {
        queue.push(event("started", best));
        void queue.flush(); // the server must see "started" before time is reported
      }
    };
    const io = new IntersectionObserver(
      (entries) => {
        for (const en of entries) {
          const id = (en.target as HTMLElement).dataset.section;
          if (!id) continue;
          if (en.isIntersecting) visibleNow.add(id);
          else visibleNow.delete(id);
        }
        pick();
      },
      { rootMargin: "0px", threshold: [0, 0.01] },
    );
    els.forEach((el) => io.observe(el));

    const onInteract = () => tracker.interaction(now());
    const interactions = ["pointerdown", "pointermove", "keydown", "scroll", "touchstart", "wheel"] as const;
    interactions.forEach((n) => window.addEventListener(n, onInteract, { passive: true }));

    const onVisibility = () => {
      if (document.visibilityState === "hidden") {
        tracker.setVisible(false, now());
        drainToQueue();
        const batch = queue.snapshot().slice(0, 50);
        if (batch.length > 0 && typeof navigator.sendBeacon === "function") {
          // Not acknowledged on purpose: the events carry ids, so if they are delivered twice the server keeps one.
          navigator.sendBeacon("/api/events", new Blob([JSON.stringify({ events: batch })], { type: "application/json" }));
        }
      } else {
        tracker.setVisible(true, now());
        tracker.interaction(now());
        void queue.flush();
      }
    };
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("pagehide", onVisibility);
    const onOnline = () => void queue.flush();
    window.addEventListener("online", onOnline);

    let sinceFlush = 0;
    const timer = window.setInterval(() => {
      tracker.tick(now());
      sinceFlush += TICK_MS;
      // optimistic completion: show the section as done as soon as the required time has been spent
      const active = tracker.active;
      if (active && !completedRef.current.has(active) && !optimisticRef.current.has(active)) {
        const sec = lesson.sections.find((s) => s.id === active);
        if (sec && sec.requiredSeconds !== null) {
          const need = sec.requiredSeconds * 1000 + (margins.current.get(active) ?? OPTIMISTIC_MARGIN_MS);
          if (tracker.totalMs(active) >= need) setOptimistic((p) => new Set(p).add(active));
        }
      }
      if (sinceFlush >= FLUSH_EVERY_MS) {
        sinceFlush = 0;
        drainToQueue();
        void queue.flush();
      }
    }, TICK_MS);

    pick();
    void queue.flush(); // events left over from a previous visit

    return () => {
      window.clearInterval(timer);
      io.disconnect();
      interactions.forEach((n) => window.removeEventListener(n, onInteract));
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("pagehide", onVisibility);
      window.removeEventListener("online", onOnline);
      drainToQueue();
      void queue.flush();
    };
  }, [lesson, userId, applyServerState]);

  // --- resume where the student left off --------------------------------------------------------------
  useEffect(() => {
    if (!showResume) return;
    const first = lesson.sections[0]?.id;
    if (initial.resumeSectionId && initial.resumeSectionId !== first) {
      const el = document.getElementById(`s-${initial.resumeSectionId}`);
      el?.scrollIntoView({ block: "start" });
    }
    const timer = window.setTimeout(() => setShowResume(false), 6000);
    return () => window.clearTimeout(timer);
    // runs once, on mount: the resume position is only applied when the page opens
  }, []);

  // --- derived state ----------------------------------------------------------------------------------
  const doneNow = new Set([...completed, ...optimistic]);
  const hasPractice = lesson.exerciseSets.length > 0;
  const percent = Math.max(serverProgress.lesson.percent, localPercent(doneNow.size, total, solved.size, hasPractice));

  // sections after the first unanswered check stay hidden until it is answered
  let lastVisible = total - 1;
  for (let i = 0; i < total; i++) {
    const s = lesson.sections[i];
    if (s && s.type === "check" && !completed.has(s.id)) {
      lastVisible = i;
      break;
    }
  }
  const unlocked = lastVisible === total - 1;

  /** Save a formula or a theorem to the formula sheet, or take it off again. */
  const toggleSaved = (sectionId: string) => {
    const saved = !bookmarked.has(sectionId);
    setBookmarked((p) => {
      const n = new Set(p);
      if (saved) n.add(sectionId);
      else n.delete(sectionId);
      return n;
    });
    void fetch("/api/formulas", {
      method: "POST",
      keepalive: true,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ lessonId: lesson.id, sectionId, saved }),
    }).then((r) => {
      if (!r.ok) setBookmarked((p) => {
        const n = new Set(p);
        if (saved) n.delete(sectionId);
        else n.add(sectionId);
        return n;
      });
    });
  };

  return (
    <div>
      <div className="sticky top-[var(--header-h)] z-30 border-b border-line bg-bg/95 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-2.5">
          <Link href="/dashboard" className="shrink-0 text-sm font-semibold text-accent hover:underline">
            ← <span className="hidden sm:inline">{t("lesson.back")}</span>
          </Link>
          <ProgressBar percent={percent} label={t("lesson.progress")} className="h-2.5" />
          <span className="w-12 shrink-0 text-right text-sm font-bold tabular-nums">{percent}%</span>
        </div>
      </div>

      <article className="mx-auto max-w-3xl px-4 pb-24 pt-8">
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">{lesson.title}</h1>
        <p className="mt-2 text-muted">{t("dashboard.minutes", { n: lesson.estMinutes })}</p>

        {showResume ? (
          <p role="status" className="fade-up mt-4 rounded-[var(--radius-sm)] bg-accent-soft px-4 py-2.5 font-medium text-accent">
            {t("lesson.resumeBanner")}
          </p>
        ) : null}
        {sessionExpired ? (
          <p role="alert" className="mt-4 rounded-[var(--radius-sm)] bg-warning-soft px-4 py-2.5 font-medium text-warning">
            {t("errors.signInRequired")}{" "}
            <Link href={`/signin?next=/learn/${lesson.id}`} className="underline">
              {t("nav.signIn")}
            </Link>
          </p>
        ) : null}

        <Card className="mt-6 bg-surface-2">
          <h2 className="text-sm font-bold uppercase tracking-wide text-muted">{t("lesson.objectives")}</h2>
          <ul className="mt-2 grid list-disc gap-1 pl-5">
            {lesson.objectivesHtml.map((html, i) => (
              <li key={i}>
                <RichInline html={html} className="rich" />
              </li>
            ))}
          </ul>
        </Card>

        <div className="mt-8 grid grid-cols-[minmax(0,1fr)] gap-8">
          {lesson.sections.slice(0, lastVisible + 1).map((s) => {
            const isDone = doneNow.has(s.id);
            return (
              <section
                key={s.id}
                id={`s-${s.id}`}
                data-section={s.id}
                className="fade-up relative min-w-0 scroll-mt-32"
                aria-label={s.type === "check" ? t("lesson.check") : undefined}
              >
                <span
                  className={`absolute -left-3 top-1 hidden h-[calc(100%-0.5rem)] w-1 rounded-full transition-colors duration-[var(--dur)] sm:block ${
                    isDone ? "bg-success" : "bg-line"
                  }`}
                  title={isDone ? t("lesson.sectionDone") : undefined}
                  aria-hidden="true"
                />
                {s.type === "concept" ? <ConceptBlock s={s} /> : null}
                {s.type === "definition" ? <DefinitionBlock s={s} /> : null}
                {s.type === "theorem" ? <TheoremBlock s={s} saved={bookmarked.has(s.id)} onToggleSaved={() => toggleSaved(s.id)} /> : null}
                {s.type === "formula" ? (
                  <FormulaBlock s={s} saved={bookmarked.has(s.id)} onToggleSaved={() => toggleSaved(s.id)} />
                ) : null}
                {s.type === "example" ? <ExampleBlock s={s} /> : null}
                {s.type === "visual" ? <VisualBlock s={s} /> : null}
                {s.type === "summary" ? <SummaryBlock s={s} /> : null}
                {s.type === "check" ? (
                  <CheckBlock
                    lessonId={lesson.id}
                    section={s}
                    completed={completed.has(s.id)}
                    hintsUsed={initial.hintsUsed[s.id] ?? 0}
                    onCorrect={(progress) => {
                      setCompleted((p) => new Set(p).add(s.id));
                      if (progress) setServerProgress(progress);
                    }}
                  />
                ) : null}
              </section>
            );
          })}
        </div>

        {lastVisible < total - 1 ? (
          <p className="mt-8 rounded-[var(--radius-sm)] border border-dashed border-line px-4 py-3 text-center text-muted">{t("lesson.locked")}</p>
        ) : null}

        {unlocked && hasPractice ? (
          <ExerciseSets
            lessonId={lesson.id}
            sets={lesson.exerciseSets}
            solved={solved}
            hintsUsed={initial.hintsUsed}
            onSolved={(id, progress) => {
              setSolved((p) => new Set(p).add(id));
              if (progress) setServerProgress(progress);
            }}
          />
        ) : null}

        {percent >= 100 ? (
          <Card className="pop mt-10 border-success text-center">
            <p className="text-xl font-bold text-success">{t("lesson.lessonDone")}</p>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              {next ? (
                <Link href={`/learn/${next.id}`} className={buttonClass("primary")}>
                  {t("lesson.next")}: {next.title}
                </Link>
              ) : null}
              <Link href="/dashboard" className={buttonClass("secondary")}>
                {t("lesson.back")}
              </Link>
            </div>
          </Card>
        ) : null}
      </article>
    </div>
  );
}

// re-exported for tests that render a single block
export { Rich };
