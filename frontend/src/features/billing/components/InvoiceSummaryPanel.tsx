import { CurrencyDisplay } from "@/design-system";
import type { InvoiceLineDraft } from "@/features/billing/components/ServiceSearchPicker";
import { computeInvoiceTotals } from "@/features/billing/utils/invoiceTotals";

interface InvoiceSummaryPanelProps {
  lines: InvoiceLineDraft[];
  pago?: number;
  className?: string;
}

export function InvoiceSummaryPanel({ lines, pago = 0, className = "" }: InvoiceSummaryPanelProps) {
  const { subtotalOficial, reducao, total } = computeInvoiceTotals(lines);
  const saldo = Math.max(0, total - pago);

  return (
    <aside
      className={`sticky top-4 space-y-4 rounded-2xl border border-border bg-surface p-5 shadow-sm ${className}`}
      aria-label="Resumo da fatura"
    >
      <h3 className="text-sm font-semibold tracking-wide text-text-muted uppercase">Resumo</h3>
      <dl className="space-y-3 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-text-muted">Subtotal (oficial)</dt>
          <dd className="font-medium tabular-nums text-text">
            <CurrencyDisplay value={subtotalOficial} />
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-text-muted">Redução</dt>
          <dd className="font-medium tabular-nums text-amber-700 dark:text-amber-400">
            {reducao > 0 ? (
              <>
                − <CurrencyDisplay value={reducao} />
              </>
            ) : (
              <span className="text-text-muted">—</span>
            )}
          </dd>
        </div>
        <div className="flex justify-between gap-4 border-t border-border pt-3">
          <dt className="font-semibold text-text">Total a cobrar</dt>
          <dd className="text-lg font-bold tabular-nums text-primary-700 dark:text-primary-300">
            <CurrencyDisplay value={total} />
          </dd>
        </div>
        {pago > 0 ? (
          <>
            <div className="flex justify-between gap-4">
              <dt className="text-text-muted">Pago</dt>
              <dd className="font-medium tabular-nums text-emerald-700 dark:text-emerald-400">
                <CurrencyDisplay value={pago} />
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="font-semibold text-text">Saldo</dt>
              <dd className="font-bold tabular-nums text-text">
                <CurrencyDisplay value={saldo} />
              </dd>
            </div>
          </>
        ) : null}
      </dl>
      <p className="text-xs leading-relaxed text-text-muted">
        O preço oficial do catálogo permanece inalterado. Reduções aplicam-se apenas a esta fatura.
      </p>
    </aside>
  );
}
