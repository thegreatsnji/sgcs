import type { CheckInStatus, QueuePriority, QueueStatus, ReferralDepartment, TriageColor } from "@/types/reception";

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

export const TRIAGE_COLOR_LABELS: Record<TriageColor, string> = {
  GREEN: "Verde",
  YELLOW: "Amarelo",
  RED: "Vermelho",
};

export const TRIAGE_COLOR_SUMMARY: Record<TriageColor, string> = {
  GREEN: "Estável",
  YELLOW: "Prioritário",
  RED: "Emergência",
};

export const TRIAGE_COLOR_DESCRIPTIONS: Record<TriageColor, string> = {
  GREEN: "O paciente pode aguardar na fila sem risco imediato.",
  YELLOW: "Requer atenção mais rápida que os casos estáveis.",
  RED: "Necessita atendimento imediato pela equipa clínica.",
};

export const TRIAGE_WAIT_LABELS: Record<TriageColor, string> = {
  GREEN: "Até 120 min",
  YELLOW: "Até 90 min",
  RED: "Imediato",
};

export const TRIAGE_WAIT_MINUTES: Record<TriageColor, number> = {
  GREEN: 120,
  YELLOW: 90,
  RED: 0,
};

export const TRIAGE_COLOR_OPTIONS = (["GREEN", "YELLOW", "RED"] as TriageColor[]).map((value) => ({
  value,
  label: TRIAGE_COLOR_LABELS[value],
  summary: TRIAGE_COLOR_SUMMARY[value],
  description: TRIAGE_COLOR_DESCRIPTIONS[value],
  waitLabel: TRIAGE_WAIT_LABELS[value],
  waitMinutes: TRIAGE_WAIT_MINUTES[value],
}));
