import type { HTMLAttributes, ReactNode } from "react";

export type BadgeVariant = "default" | "success" | "warning" | "danger" | "info";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: ReactNode;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-surface-muted text-text dark:bg-slate-700 dark:text-slate-200",
  success: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  danger: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
  info: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
};

export function Badge({ variant = "default", className = "", children, ...props }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-lg px-2.5 py-1 text-xs font-semibold ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
