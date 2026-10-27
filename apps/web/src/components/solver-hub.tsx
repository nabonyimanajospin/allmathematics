"use client";

import { useId, useState } from "react";
import { buttonClass } from "@allmaths/ui";
import { t } from "@/i18n";
import type { SolverAccessDto } from "@/lib/solver-types";
import { SolverClient } from "./solver-client";
import { TriangleTool } from "./triangle-tool";

export type SolverMode = "problem" | "triangle";

/**
 * The solver page: "Any problem" (typed, step by step) and "A triangle (three vertices)" in one place, so that the header has one link.
 * Both parts stay mounted, so that switching never loses what was typed. When the text box holds a triangle problem the learner
 * is offered the triangle toolkit, which then analyzes the points at once.
 */
export function SolverHub({ initialAccess, canPay, justPaid, initialMode }: { initialAccess: SolverAccessDto; canPay: boolean; justPaid: boolean; initialMode: SolverMode }) {
  const uid = useId();
  const [mode, setMode] = useState<SolverMode>(initialMode);
  const [handoff, setHandoff] = useState<{ points: string[][]; run: boolean; n: number } | undefined>(undefined);

  function open(next: SolverMode) {
    setMode(next);
    const url = new URL(window.location.href);
    if (next === "triangle") url.searchParams.set("mode", "triangle");
    else url.searchParams.delete("mode");
    window.history.replaceState(null, "", url);
  }

  const tabs: { mode: SolverMode; label: string }[] = [
    { mode: "problem", label: t("solver.tabProblem") },
    { mode: "triangle", label: t("solver.tabTriangle") },
  ];
  return (
    <div>
      <div role="tablist" aria-label={t("solver.tabsLabel")} className="mb-6 flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.mode}
            type="button"
            role="tab"
            id={`${uid}-tab-${tab.mode}`}
            aria-selected={mode === tab.mode}
            aria-controls={`${uid}-panel-${tab.mode}`}
            onClick={() => open(tab.mode)}
            className={buttonClass(mode === tab.mode ? "primary" : "secondary")}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`${uid}-panel-problem`} aria-labelledby={`${uid}-tab-problem`} hidden={mode !== "problem"} className="max-w-3xl">
        <SolverClient
          initialAccess={initialAccess}
          canPay={canPay}
          justPaid={justPaid}
          onTriangle={(points) => {
            setHandoff((h) => ({ points, run: true, n: (h?.n ?? 0) + 1 }));
            open("triangle");
          }}
        />
      </div>
      <div role="tabpanel" id={`${uid}-panel-triangle`} aria-labelledby={`${uid}-tab-triangle`} hidden={mode !== "triangle"}>
        <p className="mb-4 max-w-3xl text-muted">{t("triangle.lead")}</p>
        <TriangleTool key={handoff?.n ?? 0} {...(handoff ? { start: handoff } : {})} />
      </div>
    </div>
  );
}
