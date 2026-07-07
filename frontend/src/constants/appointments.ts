import type { AppointmentStatus } from "@/types/appointment";

export const APPOINTMENT_STATUS_LABELS: Record<AppointmentStatus, string> = {
  AGENDADA: "Agendada",
  CONFIRMADA: "Confirmada",
  EM_ESPERA: "Em espera",
  EM_CONSULTA: "Em consulta",
  CONCLUIDA: "Concluída",
  CANCELADA: "Cancelada",
  FALTA: "Falta",
};

export const APPOINTMENT_STATUS_VARIANT: Record<
  AppointmentStatus,
  "default" | "success" | "warning" | "danger" | "info"
> = {
  AGENDADA: "info",
  CONFIRMADA: "warning",
  EM_ESPERA: "warning",
  EM_CONSULTA: "info",
  CONCLUIDA: "success",
  CANCELADA: "default",
  FALTA: "danger",
};

export const APPOINTMENT_PAGE_SIZE = 20;

/** Alias legado para páginas /consultations */
export const CONSULTATION_PAGE_SIZE = APPOINTMENT_PAGE_SIZE;

export const PRIORITY_LABELS = {
  LOW: "Baixa",
  NORMAL: "Normal",
  HIGH: "Alta",
  EMERGENCY: "Emergência",
};
