import type { ChangeEvent } from "react";
import { forwardRef, useCallback, type InputHTMLAttributes } from "react";

export interface DisplayDateInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  error?: string;
  hint?: string;
  onValueChange?: (value: string) => void;
}

/** Formata enquanto digita: DD/MM/AAAA (só dígitos; barras automáticas). */
export function formatDisplayDateInput(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

export const DisplayDateInput = forwardRef<HTMLInputElement, DisplayDateInputProps>(
  ({ label, error, hint, className = "", id, onChange, onValueChange, value, ...props }, ref) => {
    const inputId = id ?? props.name;

    const handleChange = useCallback(
      (event: ChangeEvent<HTMLInputElement>) => {
        const formatted = formatDisplayDateInput(event.target.value);
        event.target.value = formatted;
        onValueChange?.(formatted);
        onChange?.(event);
      },
      [onChange, onValueChange],
    );

    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-text">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          type="text"
          inputMode="numeric"
          autoComplete="bday"
          placeholder="DD/MM/AAAA"
          maxLength={10}
          value={value}
          className={`w-full rounded-lg border bg-surface px-3 py-2 text-sm text-text outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900 ${
            error ? "border-red-500" : "border-border"
          } ${className}`}
          onChange={handleChange}
          {...props}
        />
        {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
        {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
      </div>
    );
  },
);

DisplayDateInput.displayName = "DisplayDateInput";
