"use client";

import { useState } from "react";
import { Button } from "@allmaths/ui";
import type { RSection } from "@/lib/lesson-types";
import { t } from "@/i18n";
import { Rich, RichInline } from "./rich";
import { VectorExplorer } from "./vector-explorer";

type Of<T extends RSection["type"]> = Extract<RSection, { type: T }>;

const label = "mb-2 text-sm font-bold uppercase tracking-wide";

export function ConceptBlock({ s }: { s: Of<"concept"> }) {
  return (
    <div>
      {s.titleHtml ? <h2 className="mb-3 text-2xl font-bold tracking-tight"><RichInline html={s.titleHtml} /></h2> : null}
      <Rich html={s.bodyHtml} />
    </div>
  );
}

export function DefinitionBlock({ s }: { s: Of<"definition"> }) {
  return (
    <div className="rounded-[var(--radius)] border border-line border-l-4 border-l-accent bg-accent-soft p-5">
      <p className={`${label} text-accent`}>{t("lesson.definition")}</p>
      <h2 className="mb-2 text-xl font-bold"><RichInline html={s.termHtml} /></h2>
      <Rich html={s.bodyHtml} />
    </div>
  );
}

export function TheoremBlock({ s }: { s: Of<"theorem"> }) {
  return (
    <div className="rounded-[var(--radius)] border border-line border-l-4 border-l-warning bg-warning-soft p-5">
      <p className={`${label} text-warning`}>
        {t("lesson.theorem")}
        {s.nameHtml ? <>: <RichInline html={s.nameHtml} /></> : null}
      </p>
      <Rich html={s.statementHtml} />
      {s.proofHtml ? (
        <details className="mt-3">
          <summary className="inline-flex min-h-10 items-center font-semibold text-accent">{t("lesson.proof")}</summary>
          <div className="mt-2 border-l-2 border-line pl-4">
            <Rich html={s.proofHtml} />
          </div>
        </details>
      ) : null}
    </div>
  );
}

export function FormulaBlock({
  s,
  bookmarked,
  onBookmark,
}: {
  s: Of<"formula">;
  bookmarked: boolean;
  onBookmark: () => void;
}) {
  return (
    <div className="rounded-[var(--radius)] border-2 border-accent bg-surface p-5">
      <p className={`${label} text-accent`}>
        {t("lesson.formula")}: <RichInline html={s.titleHtml} />
      </p>
      <div className="text-center text-lg" dangerouslySetInnerHTML={{ __html: s.formulaHtml }} />
      {s.noteHtml ? <Rich html={s.noteHtml} className="text-muted" /> : null}
      <Button variant="secondary" className="mt-3" onClick={onBookmark} disabled={bookmarked} aria-pressed={bookmarked}>
        {bookmarked ? `✓ ${t("lesson.bookmarked")}` : t("lesson.bookmark")}
      </Button>
    </div>
  );
}

export function ExampleBlock({ s }: { s: Of<"example"> }) {
  const [shown, setShown] = useState(0);
  const total = s.stepsHtml.length;
  return (
    <div className="rounded-[var(--radius)] border border-line bg-surface p-5">
      <p className={`${label} text-accent`}>
        {t("lesson.example")}
        {s.titleHtml ? <>: <RichInline html={s.titleHtml} /></> : null}
      </p>
      <Rich html={s.problemHtml} className="font-medium" />
      <ol className="mt-4 grid gap-3" aria-live="polite">
        {s.stepsHtml.slice(0, shown).map((html, i) => (
          <li key={i} className="fade-up flex gap-3">
            <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-full bg-accent-soft text-sm font-bold text-accent">{i + 1}</span>
            <Rich html={html} />
          </li>
        ))}
      </ol>
      {shown < total ? (
        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={() => setShown((n) => n + 1)}>{t("lesson.nextStep")}</Button>
          <Button variant="ghost" onClick={() => setShown(total)}>
            {t("lesson.showAll")}
          </Button>
        </div>
      ) : (
        <div className="fade-up mt-4 rounded-[var(--radius-sm)] bg-success-soft px-4 py-3">
          <p className={`${label} mb-1 text-success`}>{t("lesson.answerLabel")}</p>
          <Rich html={s.answerHtml} />
        </div>
      )}
    </div>
  );
}

export function VisualBlock({ s }: { s: Of<"visual"> }) {
  return (
    <div className="rounded-[var(--radius)] border border-line bg-surface p-5">
      <p className={`${label} text-accent`}>
        {t("lesson.visual")}: <RichInline html={s.titleHtml} />
      </p>
      <VectorExplorer mode={s.mode} />
      <Rich html={s.captionHtml} className="mt-3 text-muted" />
    </div>
  );
}

export function SummaryBlock({ s }: { s: Of<"summary"> }) {
  return (
    <div className="rounded-[var(--radius)] border border-line bg-surface-2 p-5">
      <h2 className="mb-3 text-xl font-bold">{t("lesson.summary")}</h2>
      <ul className="grid gap-3">
        {s.pointsHtml.map((html, i) => (
          <li key={i} className="flex gap-3">
            <svg className="mt-1.5 shrink-0 text-success" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M5 12.5l4.5 4.5L19 7.5" />
            </svg>
            <Rich html={html} />
          </li>
        ))}
      </ul>
    </div>
  );
}
