import type { InvoiceLineDraft } from "@/features/billing/components/ServiceSearchPicker";
import { calcReducao } from "@/features/billing/constants/reducao";

export function computeInvoiceTotals(lines: InvoiceLineDraft[]) {
  let subtotalOficial = 0;
  let subtotalCobrado = 0;

  for (const line of lines) {
    const oficial = Number(line.servico.preco);
    const unit =
      line.aplicarReducao && line.precoCobrado != null ? line.precoCobrado : oficial;
    subtotalOficial += oficial * line.quantidade;
    subtotalCobrado += unit * line.quantidade;
  }

  const reducao = Math.max(0, subtotalOficial - subtotalCobrado);
  return {
    subtotalOficial,
    subtotalCobrado,
    reducao,
    total: subtotalCobrado,
  };
}

export function lineReducao(line: InvoiceLineDraft) {
  const oficial = Number(line.servico.preco);
  const cobrado =
    line.aplicarReducao && line.precoCobrado != null ? line.precoCobrado : oficial;
  return calcReducao(oficial, cobrado);
}
