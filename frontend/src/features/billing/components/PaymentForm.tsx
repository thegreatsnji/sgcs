import { Button } from "@/design-system";
import type { MetodoPagamento } from "@/types/billing";

const METODOS: MetodoPagamento[] = ["DINHEIRO", "TRANSFERENCIA", "CARTAO", "MOBILE_MONEY", "OUTRO"];

interface PaymentFormProps {
  faturaId: number;
  valorSugerido?: string;
  onSubmit: (values: { fatura: number; metodo_pagamento: string; valor: string; referencia?: string }) => void;
  isPending?: boolean;
}

export function PaymentForm({ faturaId, valorSugerido, onSubmit, isPending }: PaymentFormProps) {
  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        onSubmit({
          fatura: faturaId,
          metodo_pagamento: String(form.get("metodo_pagamento")),
          valor: String(form.get("valor")),
          referencia: String(form.get("referencia") || ""),
        });
      }}
    >
      <div>
        <label className="mb-1 block text-sm text-slate-600">Método</label>
        <select name="metodo_pagamento" className="w-full rounded border border-slate-300 px-3 py-2 text-sm" defaultValue="DINHEIRO">
          {METODOS.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Valor (FCFA)</label>
        <input
          name="valor"
          type="number"
          step="0.01"
          defaultValue={valorSugerido}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          required
        />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Referência</label>
        <input name="referencia" className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
      </div>
      <Button type="submit" variant="primary" disabled={isPending}>
        {isPending ? "A registar..." : "Registar pagamento"}
      </Button>
    </form>
  );
}
