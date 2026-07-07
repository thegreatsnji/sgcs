import type { LaboratoryOrderStatus } from "@/types/laboratory";

export const LAB_STATUS_LABELS: Record<LaboratoryOrderStatus, string> = {
  PENDENTE: "Pendente",
  RECEBIDO: "Recebido",
  AGUARDANDO_COLHEITA: "Aguardando colheita",
  EM_PROCESSAMENTO: "Em processamento",
  CONCLUIDO: "Concluído",
  CANCELADO: "Cancelado",
};

export const LAB_STATUS_VARIANT: Record<
  LaboratoryOrderStatus,
  "default" | "success" | "warning" | "danger" | "info"
> = {
  PENDENTE: "warning",
  RECEBIDO: "info",
  AGUARDANDO_COLHEITA: "warning",
  EM_PROCESSAMENTO: "info",
  CONCLUIDO: "success",
  CANCELADO: "default",
};

export const LAB_PAGE_SIZE = 20;
