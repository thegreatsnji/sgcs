import type { BaseEntity } from "./common";

export type AppointmentStatus =
  | "AGENDADA"
  | "CONFIRMADA"
  | "EM_ESPERA"
  | "EM_CONSULTA"
  | "CONCLUIDA"
  | "CANCELADA"
  | "FALTA";

export type AppointmentPriority = "LOW" | "NORMAL" | "HIGH" | "EMERGENCY";

export interface AppointmentPatientSummary {
  id: number;
  full_name: string;
  patient_number: string;
  phone: string | null;
}

export interface AppointmentUserSummary {
  id: number;
  full_name: string;
}

export interface Appointment extends BaseEntity {
  appointment_number: string;
  patient: AppointmentPatientSummary;
  doctor: AppointmentUserSummary | null;
  receptionist: AppointmentUserSummary | null;
  queue_entry: number | null;
  check_in: number | null;
  referral: number | null;
  scheduled_at: string;
  consultation_date: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_minutes: number;
  status: AppointmentStatus;
  priority: AppointmentPriority;
  chief_complaint: string;
  notes: string;
  diagnosis: string;
  clinical_notes: string;
  cancellation_reason: string;
  created_by: AppointmentUserSummary | null;
}

export interface AppointmentCreatePayload {
  patient_id: number;
  doctor_id?: number | null;
  scheduled_at?: string;
  duration_minutes?: number;
  priority?: AppointmentPriority;
  notes?: string;
  chief_complaint?: string;
}

export interface AppointmentUpdatePayload {
  doctor?: number;
  scheduled_at?: string;
  duration_minutes?: number;
  priority?: AppointmentPriority;
  chief_complaint?: string;
  notes?: string;
}

export interface ConsultasDashboardData {
  indicadores: {
    consultas_do_dia: number;
    consultas_concluidas: number;
    consultas_em_espera: number;
    consultas_em_curso: number;
    medicos_em_servico: number;
    pedidos_laboratorio_emitidos?: number;
    pedidos_imagiologia_emitidos?: number;
  };
  proxima_consulta: {
    id: number;
    appointment_number: string;
    patient: string;
    doctor: string | null;
    scheduled_at: string;
  } | null;
  cards: {
    waiting_for_doctor: number;
    in_progress: number;
    completed_today: number;
    scheduled_today: number;
    lab_orders_today?: number;
    imaging_orders_today?: number;
  };
  queue_preview: Array<{
    id: number;
    appointment_number: string;
    status: string;
    scheduled_at: string;
    patient__full_name: string;
    patient__patient_number: string;
  }>;
  recent_consultation_activity: Array<{
    action: string;
    description: string;
    user: string;
    created_at: string;
  }>;
}

/** Alias legado — compatível com dashboard /consultations/ */
export type ConsultationDashboardData = ConsultasDashboardData;
