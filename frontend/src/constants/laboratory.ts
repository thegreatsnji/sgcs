import type { LabEstadoFaturacao, LaboratoryOrderStatus } from "@/types/laboratory";

export const LAB_STATUS_LABELS: Record<LaboratoryOrderStatus, string> = {
  PENDENTE: "Pendente",
  RECEBIDO: "Recebido",
  AGUARDANDO_COLHEITA: "Colheita registada",
  EM_PROCESSAMENTO: "Em processamento",
  CONCLUIDO: "Processamento concluído",
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

export const LAB_FATURACAO_LABELS: Record<LabEstadoFaturacao, string> = {
  AGUARDA_REGULARIZACAO: "Aguarda regularização",
  REGULARIZADO: "Regularizado",
  NAO_APLICAVEL: "N/A",
};

export const LAB_PAGE_SIZE = 20;
