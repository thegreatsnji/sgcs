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
    <div className="rounded-xl border border-border bg-surface p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-text-muted">{label}</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight text-text tabular-nums">{value}</p>
          {trend && <p className="mt-1 text-xs text-text-muted">{trend}</p>}
        </div>
        {icon && (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-900/40 dark:text-primary-300">
            {icon}
          </div>
        )}
      </div>
      {badge && (
        <div className="mt-3">
          <Badge variant={badge.variant ?? "default"}>{badge.text}</Badge>
        </div>
      )}
    </div>
  );
}
