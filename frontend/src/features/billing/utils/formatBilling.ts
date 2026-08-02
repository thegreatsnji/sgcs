import type { FaturaEstado, MetodoPagamento, PagamentoEstado } from "@/types/billing";

export function formatCurrency(value: string | number): string {
  const num = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(num)) return "—";
  return `${num.toLocaleString("pt-PT")} FCFA`;
}

export const FATURA_ESTADO_LABEL: Record<FaturaEstado, string> = {
  PENDENTE: "Pendente",
  PARCIAL: "Parcialmente paga",
  PAGA: "Paga",
  CANCELADA: "Cancelada",
};

export const FATURA_ESTADO_VARIANT: Record<FaturaEstado, "default" | "success" | "warning" | "danger" | "info"> = {
  PENDENTE: "warning",
  PARCIAL: "info",
  PAGA: "success",
  CANCELADA: "default",
};

export const PAGAMENTO_ESTADO_LABEL: Record<PagamentoEstado, string> = {
  PENDENTE: "Pendente",
  PROCESSADO: "Processado",
  CONFIRMADO: "Confirmado",
  REEMBOLSADO: "Reembolsado",
};

export const METODO_PAGAMENTO_LABEL: Record<MetodoPagamento, string> = {
  DINHEIRO: "Dinheiro",
  TRANSFERENCIA: "Transferência",
  CARTAO: "Cartão",
  MOBILE_MONEY: "Mobile Money",
  OUTRO: "Outro",
};
