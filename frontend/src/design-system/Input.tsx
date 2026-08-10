import type { InputHTMLAttributes } from "react";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

function FieldError({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm leading-snug text-red-800 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-200"
    >
      <span
        className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-red-600 text-xs font-bold text-white"
        aria-hidden
      >
        !
      </span>
      <span>{message}</span>
    </div>
  );
}

export function Input({ label, error, hint, className = "", id, ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-text">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full rounded-lg border bg-surface px-3 py-2 text-sm text-text outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900 ${
          error ? "border-red-500 ring-1 ring-red-500/25" : "border-border"
        } ${className}`}
        {...props}
      />
      {error ? <FieldError message={error} /> : null}
      {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
    </div>
  );
}
