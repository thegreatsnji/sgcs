import type { InputHTMLAttributes } from "react";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function Input({ label, error, hint, className = "", id, ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-text">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full rounded-lg border bg-surface px-3 py-2 text-sm text-text outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900 ${
          error ? "border-red-500" : "border-border"
        } ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
      {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
    </div>
  );
}
