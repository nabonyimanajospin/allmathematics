/**
 * Shared presentational components. No data fetching, no business rules: those live in services.
 * Styling uses Tailwind classes bound to the design tokens (bg-surface, text-ink, ...).
 */

import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from "react";

export function cn(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(" ");
}

// --- Button ---------------------------------------------------------------------------------------
type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

const buttonBase =
  "inline-flex min-h-11 items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-sm)] px-4 py-2 text-[0.95rem] font-semibold " +
  "transition-colors duration-[var(--dur-fast)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--focus)] " +
  "disabled:cursor-not-allowed disabled:opacity-55";

const buttonVariants: Record<ButtonVariant, string> = {
  primary: "bg-accent text-on-accent hover:bg-accent-strong",
  secondary: "border border-line bg-surface text-ink hover:bg-surface-2",
  ghost: "text-accent hover:bg-accent-soft",
  danger: "bg-danger text-on-accent hover:opacity-90",
};

export function buttonClass(variant: ButtonVariant = "primary", extra?: string): string {
  return cn(buttonBase, buttonVariants[variant], extra);
}

export function Button({
  variant = "primary",
  className,
  type = "button",
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }) {
  return <button type={type} className={buttonClass(variant, className)} {...rest} />;
}

// --- Card -----------------------------------------------------------------------------------------
export function Card({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-[var(--radius)] border border-line bg-surface p-5 shadow-[var(--shadow-sm)]", className)}
      {...rest}
    />
  );
}

// --- Progress -------------------------------------------------------------------------------------
export interface ProgressBarProps {
  /** Percentage 0..100 (a fraction is allowed). */
  percent: number;
  label: string;
  className?: string;
  tone?: "accent" | "success";
}

export function ProgressBar({ percent, label, className, tone = "success" }: ProgressBarProps) {
  // the bar may carry a fraction of a percent so that small real progress is visible
  const p = Math.max(0, Math.min(100, percent >= 100 ? 100 : Math.floor(percent * 10) / 10));
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={p}
      className={cn("h-2 w-full overflow-hidden rounded-full bg-surface-2", className)}
    >
      <div
        className={cn("h-full rounded-full transition-[width] duration-[var(--dur-slow)] ease-[var(--ease)]", tone === "success" ? "bg-success" : "bg-accent")}
        style={{ width: `${p}%` }}
      />
    </div>
  );
}

export interface ProgressRingProps {
  percent: number;
  label: string;
  size?: number;
  children?: ReactNode;
  /** Green for the learner's own progress, blue otherwise. */
  tone?: "accent" | "success";
}

export function ProgressRing({ percent, label, size = 96, children, tone = "accent" }: ProgressRingProps) {
  const p = Math.max(0, Math.min(100, Math.floor(percent)));
  const stroke = Math.max(6, Math.round(size / 11));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={p}
      className="relative inline-grid place-items-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90" aria-hidden="true">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" strokeWidth={stroke} stroke="var(--line)" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          stroke={tone === "success" ? "var(--success)" : "var(--accent)"}
          strokeDasharray={c}
          strokeDashoffset={c * (1 - p / 100)}
          style={{ transition: "stroke-dashoffset var(--dur-slow) var(--ease)" }}
        />
      </svg>
      <span className="absolute text-center text-lg font-bold tabular-nums text-ink">{children ?? `${p}%`}</span>
    </div>
  );
}

// --- Skeleton -------------------------------------------------------------------------------------
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={cn("rounded-[var(--radius-sm)]", className)}
      style={{
        background: "linear-gradient(90deg, var(--surface-2) 25%, var(--line) 50%, var(--surface-2) 75%)",
        backgroundSize: "200% 100%",
        animation: "am-shimmer 1.4s linear infinite",
      }}
    />
  );
}

// --- Form field -----------------------------------------------------------------------------------
export function Field({
  label,
  id,
  hint,
  error,
  children,
}: {
  label: string;
  id: string;
  hint?: string | undefined;
  error?: string | undefined;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-1.5">
      <label htmlFor={id} className="text-sm font-semibold text-ink">
        {label}
      </label>
      {children}
      {hint && !error ? (
        <p id={`${id}-hint`} className="text-sm text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={`${id}-error`} role="alert" className="text-sm font-medium text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export const inputClass =
  "min-h-11 w-full rounded-[var(--radius-sm)] border border-line bg-surface px-3 py-2 text-base text-ink " +
  "placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[var(--focus)]";

// --- Logo -----------------------------------------------------------------------------------------
export function Logo({ name }: { name: string }) {
  return (
    <span className="inline-flex items-center gap-2 font-bold tracking-tight text-ink">
      <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
        <rect width="26" height="26" rx="7" fill="var(--accent)" />
        <path d="M6 18 L13 7 L20 18" fill="none" stroke="var(--on-accent)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M9 14.5h8" stroke="var(--on-accent)" strokeWidth="2.4" strokeLinecap="round" />
      </svg>
      <span>{name}</span>
    </span>
  );
}
