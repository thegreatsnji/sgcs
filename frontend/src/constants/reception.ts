import type { CheckInStatus, QueuePriority, QueueStatus, ReferralDepartment } from "@/types/reception";

export const QUEUE_PRIORITY_LABELS: Record<QueuePriority, string> = {
  LOW: "Baixa",
  NORMAL: "Normal",
  HIGH: "Alta",
  EMERGENCY: "Emergência",
};

export const QUEUE_STATUS_LABELS: Record<QueueStatus, string> = {
  WAITING: "Em espera",
  CALLED: "Chamado",
  IN_SERVICE: "Em atendimento",
  COMPLETED: "Concluído",
  CANCELLED: "Cancelado",
};

export const CHECK_IN_STATUS_LABELS: Record<CheckInStatus, string> = {
  WAITING: "Em espera",
  IN_CONSULTATION: "Em consulta",
  COMPLETED: "Concluído",
  CANCELLED: "Cancelado",
};

export const REFERRAL_DEPARTMENT_LABELS: Record<ReferralDepartment, string> = {
  RECEPTION: "Receção",
  DOCTOR: "Médico",
  LAB: "Laboratório",
  BILLING: "Faturação",
};

export const PRIORITY_OPTIONS = Object.entries(QUEUE_PRIORITY_LABELS).map(([value, label]) => ({
  value,
  label,
}));

export const REFERRAL_DEPARTMENT_OPTIONS = (
  ["DOCTOR", "LAB", "BILLING"] as ReferralDepartment[]
).map((value) => ({
  value,
  label: REFERRAL_DEPARTMENT_LABELS[value],
}));

export const QUEUE_STATUS_OPTIONS = Object.entries(QUEUE_STATUS_LABELS).map(([value, label]) => ({
  value,
  label,
}));

export const RECEPTION_PAGE_SIZE = 20;
