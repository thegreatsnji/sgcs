import type { ReactNode } from "react";

import { Badge } from "@/design-system";

interface KpiCardProps {
  label: string;
  value: string | number;
  badge?: { text: string; variant?: "success" | "warning" | "danger" | "info" | "default" };
  icon?: ReactNode;
  trend?: string;
}

export function KpiCard({ label, value, badge, icon, trend }: KpiCardProps) {
  return (
    <div className="group rounded-2xl border border-border bg-surface/90 p-5 shadow-sm backdrop-blur-sm transition hover:-translate-y-0.5 hover:border-primary-300/60 hover:shadow-md dark:hover:border-primary-500/40">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-semibold tracking-[0.14em] text-text-muted uppercase">{label}</p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-text tabular-nums">{value}</p>
          {trend && <p className="mt-1.5 text-xs leading-snug text-text-muted">{trend}</p>}
        </div>
        {icon && (
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-600 transition group-hover:bg-primary-100 dark:bg-primary-900/40 dark:text-primary-300 dark:group-hover:bg-primary-900/60">
            {icon}
          </div>
        )}
      </div>
      {badge && (
        <div className="mt-4">
          <Badge variant={badge.variant ?? "default"}>{badge.text}</Badge>
        </div>
      )}
    </div>
  );
}
