import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";

export interface RoleDashboardHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  tone?: "emerald" | "violet" | "amber" | "teal" | "primary" | "slate";
  primaryAction?: { to: string; label: string };
  secondaryAction?: { to: string; label: string };
  footer?: ReactNode;
}

const TONE_CLASSES: Record<NonNullable<RoleDashboardHeroProps["tone"]>, string> = {
  emerald: "border-emerald-500/25 bg-gradient-to-br from-emerald-600 to-emerald-900",
  violet: "border-violet-500/25 bg-gradient-to-br from-violet-600 via-violet-800 to-slate-900",
  amber: "border-amber-500/25 bg-gradient-to-br from-amber-500 to-slate-900",
  teal: "border-teal-500/25 bg-gradient-to-br from-teal-600 to-slate-900",
  primary: "border-primary-500/25 bg-gradient-to-br from-primary-600 via-primary-700 to-slate-900",
  slate: "border-slate-500/25 bg-gradient-to-br from-slate-700 to-slate-900",
};

export function RoleDashboardHero({
  eyebrow,
  title,
  description,
  tone = "primary",
  primaryAction,
  secondaryAction,
  footer,
}: RoleDashboardHeroProps) {
  const navigate = useNavigate();

  return (
    <div className={`rounded-2xl border p-6 text-white shadow-md sm:p-8 ${TONE_CLASSES[tone]}`}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-[0.2em] uppercase opacity-90">{eyebrow}</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
          <p className="mt-2 max-w-xl text-sm opacity-95">{description}</p>
        </div>
        <div className="relative z-10 flex shrink-0 flex-wrap gap-2">
          {secondaryAction ? (
            <button
              type="button"
              onClick={() => navigate(secondaryAction.to)}
              className="inline-flex items-center rounded-xl border border-white/30 bg-white/10 px-4 py-2.5 text-sm font-semibold transition hover:bg-white/20 focus-ring"
            >
              {secondaryAction.label}
            </button>
          ) : null}
          {primaryAction ? (
            <button
              type="button"
              onClick={() => navigate(primaryAction.to)}
              className="inline-flex items-center rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-slate-900 shadow-sm hover:bg-slate-50 focus-ring"
            >
              {primaryAction.label}
            </button>
          ) : null}
        </div>
      </div>
      {footer ? <div className="mt-4 text-xs opacity-85">{footer}</div> : null}
    </div>
  );
}
