import type { ReactNode } from "react";

import { TYPO } from "@/constants/typography";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  variant?: "default" | "hero" | "dark";
}

const variantClasses = {
  default: "border border-border bg-surface p-6 shadow-sm sm:p-8",
  hero: "border border-border bg-gradient-to-br from-primary-50 via-surface to-surface-muted p-6 shadow-sm sm:p-8 dark:from-primary-900 dark:via-surface dark:to-surface-muted",
  dark: "border border-primary-800/40 bg-gradient-to-br from-primary-600 via-primary-700 to-slate-900 p-6 text-white shadow-lg shadow-primary-900/20 sm:p-8",
};

export function PageHeader({ eyebrow, title, description, actions, variant = "default" }: PageHeaderProps) {
  const isDark = variant === "dark";

  return (
    <div className={`rounded-2xl ${variantClasses[variant]}`}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          {eyebrow && (
            <p className={`${TYPO.eyebrow} ${isDark ? "text-primary-100/90" : ""}`}>{eyebrow}</p>
          )}
          <h1 className={`mt-1 ${TYPO.pageTitle} ${isDark ? "text-white" : ""}`}>{title}</h1>
          {description && (
            <p
              className={`mt-2 max-w-2xl ${TYPO.bodyMuted} ${isDark ? "text-primary-100/90" : ""}`}
            >
              {description}
            </p>
          )}
        </div>
        {actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}
      </div>
    </div>
  );
}
