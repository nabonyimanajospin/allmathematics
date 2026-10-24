"use client";

import Link from "next/link";
import { useId, useState } from "react";
import type { CourseOutline } from "@allmaths/server";
import { ProgressBar } from "@allmaths/ui";
import { t } from "@/i18n";

/**
 * The course outline beside a lesson: every module, unit and lesson of the course with the student's progress,
 * the lesson being read highlighted, and a search box. It follows the layout students know from a course player.
 */
export function CourseOutlinePanel({ outline }: { outline: CourseOutline }) {
  const searchId = useId();
  const [query, setQuery] = useState("");
  const q = query.trim().toLowerCase();
  const matches = (title: string) => q === "" || title.toLowerCase().includes(q);

  return (
    <nav aria-label={t("outline.title")} className="px-4 py-5">
      <p className="text-xs font-bold uppercase tracking-wide text-muted">{t("outline.title")}</p>
      <p className="mt-1 text-lg font-bold leading-snug">{outline.title}</p>
      <div className="mt-2 flex items-center gap-3">
        <ProgressBar percent={outline.percent} label={t("outline.courseProgress")} />
        <span className="w-10 shrink-0 text-right text-sm font-bold tabular-nums">{outline.percent}%</span>
      </div>

      <label htmlFor={searchId} className="sr-only">
        {t("outline.search")}
      </label>
      <input
        id={searchId}
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={t("outline.search")}
        className="mt-4 min-h-11 w-full rounded-[var(--radius-sm)] border border-line bg-bg px-3 text-base"
      />

      <ul className="mt-4 grid gap-2">
        {outline.modules.map((m) => {
          const units = m.units
            .map((u) => ({ ...u, lessons: u.lessons.filter((l) => matches(l.title) || matches(u.title) || matches(m.title)) }))
            .filter((u) => u.lessons.length > 0);
          if (units.length === 0) return null;
          return (
            <li key={m.id}>
              <details open={m.current || q !== ""} className="group rounded-[var(--radius-sm)] border border-line bg-surface">
                <summary className="flex min-h-14 cursor-pointer list-none items-center gap-3 px-3 py-2">
                  <span className="min-w-0 flex-1">
                    <span className="block font-bold leading-snug">{m.title}</span>
                    <span className="mt-1.5 flex items-center gap-2">
                      <ProgressBar percent={m.percent} label={`${m.title}: ${t("outline.moduleProgress")}`} className="h-1.5" />
                      <span className="w-9 shrink-0 text-right text-xs font-semibold tabular-nums text-muted">{m.percent}%</span>
                    </span>
                  </span>
                  <svg className="shrink-0 transition-transform group-open:rotate-180" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M6 9l6 6 6-6" />
                  </svg>
                </summary>
                <div className="border-t border-line px-2 py-2">
                  {units.map((u) => (
                    <div key={u.id} className="mb-2 last:mb-0">
                      <p className="px-2 py-1 text-xs font-bold uppercase tracking-wide text-muted">{u.title}</p>
                      <ul>
                        {u.lessons.map((l) => (
                          <li key={l.id}>
                            <Link
                              href={`/learn/${l.id}`}
                              aria-current={l.current ? "page" : undefined}
                              className={`flex min-h-11 items-center gap-2.5 rounded-[var(--radius-sm)] px-2 py-1.5 text-sm leading-snug hover:bg-surface-2 ${
                                l.current ? "bg-accent-soft font-bold text-accent" : ""
                              }`}
                            >
                              <span
                                className={`grid size-5 shrink-0 place-items-center rounded-full border text-[11px] font-bold ${
                                  l.percent >= 100 ? "border-success bg-success text-white" : "border-line text-transparent"
                                }`}
                                aria-hidden="true"
                              >
                                ✓
                              </span>
                              <span className="min-w-0 flex-1">{l.title}</span>
                              <span className="shrink-0 text-xs tabular-nums text-muted">
                                {l.percent >= 100 ? t("outline.done") : l.percent > 0 ? `${l.percent}%` : ""}
                              </span>
                            </Link>
                          </li>
                        ))}
                        {u.test ? (
                          <li>
                            <Link
                              href={`/test/${u.id}`}
                              className="mt-1 flex min-h-11 items-center gap-2.5 rounded-[var(--radius-sm)] border border-dashed border-line px-2 py-1.5 text-sm font-semibold leading-snug hover:bg-surface-2"
                            >
                              <span
                                className={`grid size-5 shrink-0 place-items-center rounded-full border text-[11px] font-bold ${
                                  u.test.passed ? "border-success bg-success text-white" : "border-accent text-accent"
                                }`}
                                aria-hidden="true"
                              >
                                {u.test.passed ? "✓" : "?"}
                              </span>
                              <span className="min-w-0 flex-1">{t("unitTest.open")}</span>
                              <span className="shrink-0 text-xs tabular-nums text-muted">
                                {u.test.passed ? t("unitTest.passedBadge") : u.test.attempts > 0 ? t("unitTest.best", { best: u.test.bestScore ?? 0, n: 10 }) : t("unitTest.notTaken")}
                              </span>
                            </Link>
                          </li>
                        ) : null}
                      </ul>
                    </div>
                  ))}
                </div>
              </details>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
