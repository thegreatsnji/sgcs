import type { HTMLAttributes, ReactNode } from "react";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  children?: ReactNode;
}

export function Card({ title, description, children, className = "", ...props }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-border bg-surface p-6 shadow-sm ${className}`}
      {...props}
    >
      {(title || description) && (
        <div className="mb-4">
          {title && <h3 className="text-lg font-semibold text-text">{title}</h3>}
          {description && <p className="mt-1 text-sm text-text-muted">{description}</p>}
        </div>
      )}
      {children}
    </div>
  );
}
