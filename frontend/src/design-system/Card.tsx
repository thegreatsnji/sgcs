import type { HTMLAttributes, ReactNode } from "react";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  footer?: ReactNode;
  children?: ReactNode;
}

export function Card({
  title,
  description,
  footer,
  children,
  className = "",
  ...props
}: CardProps) {
  return (
    <div
      className={`rounded-xl border border-border bg-surface shadow-sm ${className}`}
      {...props}
    >
      {(title || description) && (
        <div className="border-b border-border-subtle px-6 py-4">
          {title && <h3 className="text-base font-semibold text-text">{title}</h3>}
          {description && <p className="mt-1 text-sm text-text-muted">{description}</p>}
        </div>
      )}
      {children && <div className="px-6 py-5">{children}</div>}
      {footer && <div className="border-t border-border-subtle px-6 py-4">{footer}</div>}
    </div>
  );
}
