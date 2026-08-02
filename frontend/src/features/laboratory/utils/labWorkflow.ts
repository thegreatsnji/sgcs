import type { LaboratoryOrderStatus } from "@/types/laboratory";

export const LAB_WORKFLOW_STEPS: { status: LaboratoryOrderStatus; label: string }[] = [
  { status: "PENDENTE", label: "Pendente" },
  { status: "RECEBIDO", label: "Recebido" },
  { status: "AGUARDANDO_COLHEITA", label: "Colheita" },
  { status: "EM_PROCESSAMENTO", label: "Processamento" },
  { status: "CONCLUIDO", label: "Concluído" },
];

const STATUS_ORDER: LaboratoryOrderStatus[] = [
  "PENDENTE",
  "RECEBIDO",
  "AGUARDANDO_COLHEITA",
  "EM_PROCESSAMENTO",
  "CONCLUIDO",
  "CANCELADO",
];

export function getWorkflowProgress(status: LaboratoryOrderStatus): number {
  if (status === "CANCELADO") return 0;
  const index = STATUS_ORDER.indexOf(status);
  if (index < 0) return 0;
  return Math.round((index / (STATUS_ORDER.length - 2)) * 100);
}

export function getWorkflowStepIndex(status: LaboratoryOrderStatus): number {
  if (status === "CANCELADO") return -1;
  return STATUS_ORDER.indexOf(status);
}
