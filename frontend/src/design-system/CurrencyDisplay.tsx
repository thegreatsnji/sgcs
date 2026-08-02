import type { HTMLAttributes } from "react";

import { formatCurrencyAmount } from "@/utils/currency";

export interface CurrencyDisplayProps extends HTMLAttributes<HTMLSpanElement> {
  value: string | number | null | undefined;
  /** Quando true, valores negativos são apresentados entre parêntesis. */
  showNegativeInParens?: boolean;
}

export function CurrencyDisplay({
  value,
  showNegativeInParens = false,
  className = "",
  ...props
}: CurrencyDisplayProps) {
  const num = typeof value === "string" ? Number(value) : value;
  const isNegative = typeof num === "number" && Number.isFinite(num) && num < 0;
  const formatted = formatCurrencyAmount(isNegative ? Math.abs(num) : value);

  return (
    <span
      className={`tabular-nums ${isNegative ? "text-red-700" : ""} ${className}`.trim()}
      {...props}
    >
      {showNegativeInParens && isNegative ? `(${formatted})` : formatted}
    </span>
  );
}

export { formatCurrencyAmount };
