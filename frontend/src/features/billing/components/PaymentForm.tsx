import { Button } from "@/design-system";
import { METODO_PAGAMENTO_LABEL } from "@/features/billing/utils/formatBilling";
import type { MetodoPagamento } from "@/types/billing";

const METODOS: MetodoPagamento[] = ["DINHEIRO", "TRANSFERENCIA", "CARTAO", "MOBILE_MONEY", "OUTRO"];

interface PaymentFormProps {
  faturaId: number;
  valorSugerido?: string;
  saldoMaximo?: number;
  onSubmit: (values: { fatura: number; metodo_pagamento: string; valor: string; referencia?: string }) => void;
  isPending?: boolean;
  /** CTA label — atendimento uses one-click pay+recibo. */
  submitLabel?: string;
}

export function PaymentForm({
  faturaId,
  valorSugerido,
  saldoMaximo,
  onSubmit,
  isPending,
  submitLabel = "Registar pagamento",
}: PaymentFormProps) {
  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        const valor = String(form.get("valor"));
        const num = Number(valor);
        if (!Number.isFinite(num) || num <= 0) {
          e.currentTarget.reportValidity();
          return;
        }
        if (saldoMaximo != null && num > saldoMaximo + 1e-9) {
          const input = e.currentTarget.elements.namedItem("valor") as HTMLInputElement | null;
          input?.setCustomValidity("O valor do pagamento não pode ser superior ao saldo da fatura.");
          input?.reportValidity();
          input?.setCustomValidity("");
          return;
        }
        onSubmit({
          fatura: faturaId,
          metodo_pagamento: String(form.get("metodo_pagamento")),
          valor,
          referencia: String(form.get("referencia") || ""),
        });
      }}
    >
      <div>
        <label className="mb-1 block text-sm text-slate-600">Método</label>
        <select
          name="metodo_pagamento"
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          defaultValue="DINHEIRO"
        >
          {METODOS.map((m) => (
            <option key={m} value={m}>
              {METODO_PAGAMENTO_LABEL[m]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Valor (FCFA)</label>
        <input
          name="valor"
          type="number"
          step="0.01"
          min="0.01"
          max={saldoMaximo != null ? String(saldoMaximo) : undefined}
          defaultValue={valorSugerido}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          required
          onInput={(e) => e.currentTarget.setCustomValidity("")}
        />
        {saldoMaximo != null ? (
          <p className="mt-1 text-xs text-slate-500">Saldo disponível: {saldoMaximo.toLocaleString("pt-PT")} FCFA</p>
        ) : null}
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Referência</label>
        <input name="referencia" className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
      </div>
      <Button type="submit" variant="primary" disabled={isPending}>
        {isPending ? "A processar..." : submitLabel}
      </Button>
    </form>
  );
}
