import { CURRENCY_SYMBOL } from "@/constants/app";

/** Formata um valor numérico em FCFA (ex.: "5 000 FCFA"). */
export function formatCurrencyAmount(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const num = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(num)) return "—";
  return `${num.toLocaleString("pt-PT")} ${CURRENCY_SYMBOL}`;
}
