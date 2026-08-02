import { forwardRef, type InputHTMLAttributes } from "react";

import { GB_COUNTRY_CODE, GB_PHONE_LOCAL_PLACEHOLDER } from "@/constants/phone";
import { sanitizeLocalPhoneInput } from "@/utils/phone";

export interface PhoneInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  error?: string;
  hint?: string;
}

export const PhoneInput = forwardRef<HTMLInputElement, PhoneInputProps>(
  ({ label, error, hint, className = "", id, onChange, ...props }, ref) => {
    const inputId = id ?? props.name;

    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-text">
            {label}
          </label>
        )}
        <div
          className={`flex overflow-hidden rounded-lg border bg-surface transition focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-100 dark:focus-within:ring-primary-900 ${
            error ? "border-red-500" : "border-border"
          }`}
        >
          <span className="flex shrink-0 items-center border-r border-border bg-surface-muted px-3 text-sm font-semibold text-text-muted tabular-nums">
            {GB_COUNTRY_CODE}
          </span>
          <input
            ref={ref}
            id={inputId}
            type="tel"
            inputMode="numeric"
            autoComplete="tel-national"
            placeholder={GB_PHONE_LOCAL_PLACEHOLDER}
            className={`min-w-0 flex-1 bg-transparent px-3 py-2 text-sm text-text outline-none tabular-nums ${className}`}
            onChange={(event) => {
              const sanitized = sanitizeLocalPhoneInput(event.target.value);
              event.target.value = sanitized;
              onChange?.(event);
            }}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
        {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
      </div>
    );
  },
);

PhoneInput.displayName = "PhoneInput";
