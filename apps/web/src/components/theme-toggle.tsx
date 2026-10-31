"use client";

import { useEffect, useState } from "react";
import { t } from "@/i18n";

type Mode = "system" | "light" | "dark";
const ORDER: Mode[] = ["light", "dark", "system"];
const KEY = "allmaths-theme";

function apply(mode: Mode): void {
  const root = document.documentElement;
  if (mode === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", mode);
}

export function ThemeToggle() {
  const [mode, setMode] = useState<Mode>("light");

  useEffect(() => {
    try {
      const saved = localStorage.getItem(KEY);
      if (saved === "light" || saved === "dark" || saved === "system") setMode(saved);
    } catch {
      /* storage unavailable: stay on the light theme */
    }
  }, []);

  const next = ORDER[(ORDER.indexOf(mode) + 1) % ORDER.length] ?? "light";
  const label: Record<Mode, string> = {
    system: t("nav.themeSystem"),
    light: t("nav.themeLight"),
    dark: t("nav.themeDark"),
  };

  return (
    <button
      type="button"
      className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-[var(--radius-sm)] text-ink hover:bg-surface-2"
      aria-label={`${t("nav.theme")}: ${label[mode]}`}
      title={`${t("nav.theme")}: ${label[mode]}`}
      onClick={() => {
        setMode(next);
        apply(next);
        try {
          localStorage.setItem(KEY, next);
        } catch {
          /* ignore */
        }
      }}
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
        {mode === "dark" ? (
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
        ) : mode === "light" ? (
          <>
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
          </>
        ) : (
          <>
            <circle cx="12" cy="12" r="9" />
            <path d="M12 3v18" />
            <path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none" />
          </>
        )}
      </svg>
    </button>
  );
}
